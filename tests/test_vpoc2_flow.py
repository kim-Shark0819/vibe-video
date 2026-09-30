"""목 모드로 ①~⑤ 전체 흐름과 주요 규칙을 확인한다. 모델 호출 0, 비용 0."""
from __future__ import annotations

import os
import sys
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "AI-POC-whynot", "app", "src"))
sys.path.insert(0, os.path.join(ROOT, "tools"))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from vpoc2 import settings, store

    monkeypatch.setattr(settings, "ENABLED", True)
    monkeypatch.setattr(settings, "MOCK", True)
    monkeypatch.setattr(settings, "LOCAL_DIR", str(tmp_path))
    monkeypatch.setattr(settings, "MOCK_SHOT_SECONDS", 0.0)
    store.set_store(store.LocalStore(str(tmp_path)))
    import dev_server

    app = dev_server.create_app()
    return app.test_client()


def wait_task(c, run_id, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        run = c.get(f"/api/vpoc2/runs/{run_id}").get_json()["run"]
        if run["task"]["status"] != "running":
            return run
        time.sleep(0.05)
    raise AssertionError("task timeout")


def test_full_flow(client):
    c = client
    r = c.post("/api/vpoc2/runs", json={"command": "비 오는 밤 골목에서 우산을 든 여자가 기다리다가 미소 짓는다"})
    run_id = r.get_json()["run"]["id"]
    assert "_" not in run_id

    # ② 해석
    assert c.post(f"/api/vpoc2/runs/{run_id}/run/interpret").status_code == 202
    run = wait_task(c, run_id)
    assert run["task"]["status"] == "done", run["task"]
    interp = run["interpretation"]
    assert interp["status"] == "ready" and interp["violations"] == []
    assert len(interp["data"]["shots"]) == 3
    covered = {e for s in interp["data"]["shots"] for e in s["elementIds"]}
    assert covered == {e["id"] for e in interp["data"]["elements"]}

    # ③ 캐릭터 — 확정 전에는 영상 준비 불가
    assert c.post(f"/api/vpoc2/runs/{run_id}/run/draw", json={}).status_code == 202
    run = wait_task(c, run_id)
    items = run["characters"]["items"]
    assert items and all(it["image"] and it["image"]["url"] for it in items)
    resp = c.post(f"/api/vpoc2/runs/{run_id}/run/prepare")
    assert resp.status_code == 409 and resp.get_json()["error"]["type"] == "PreconditionFailed"

    # 다시 그리기(의견) → 버전 2
    cid = items[0]["id"]
    c.post(f"/api/vpoc2/runs/{run_id}/run/draw", json={"charId": cid, "feedbackKo": "머리를 더 길게"})
    run = wait_task(c, run_id)
    assert len(run["characters"]["items"][0]["history"]) == 2
    for it in run["characters"]["items"]:
        assert c.post(f"/api/vpoc2/runs/{run_id}/characters/{it['id']}/confirm", json={"confirmed": True}).status_code == 200

    # ④ 준비 → 프롬프트 3개, 검사 통과
    assert c.post(f"/api/vpoc2/runs/{run_id}/run/prepare").status_code == 202
    run = wait_task(c, run_id)
    prompts = run["video"]["prompts"]
    assert len(prompts) == 3 and all(not p["reviewKo"] for p in prompts)
    look = run["characters"]["items"][0]["appearanceShortEn"]
    assert all(look in p["promptEn"] for p in prompts if cid in
               next(s for s in run["interpretation"]["data"]["shots"] if s["id"] == p["shotId"])["characters"])

    # 금액 불일치 거절
    bad = c.post(f"/api/vpoc2/runs/{run_id}/run/generate", json={"resolution": "540p", "confirmUsd": 1})
    assert bad.status_code == 409 and bad.get_json()["error"]["type"] == "CostMismatch"
    ok = c.post(f"/api/vpoc2/runs/{run_id}/run/generate", json={"resolution": "540p", "confirmUsd": 11.25})
    assert ok.status_code == 200

    # 조회를 반복하면 동시 1개씩 제출 → 완료 → 합본
    end = time.time() + 120
    while time.time() < end:
        run = c.get(f"/api/vpoc2/runs/{run_id}").get_json()["run"]
        submitted = sum(1 for s in run["video"]["shots"] if s["status"] == "submitted")
        assert submitted <= 1
        if run["video"]["final"]["status"] == "ready":
            break
        time.sleep(0.05)
    assert run["video"]["status"] == "done"
    assert run["video"]["final"]["url"]
    final = c.get(run["video"]["final"]["url"])
    assert final.status_code == 200 and len(final.data) > 10000
    assert run["maxStep"] == 5 and run["step"] == 4

    # ⑤ 리뷰 — 요소를 다 고르지 않으면 거절
    elements = run["interpretation"]["data"]["elements"]
    partial = c.put(f"/api/vpoc2/runs/{run_id}/review", json={"score": 4, "elements": {}})
    assert partial.status_code == 400
    marks = {e["id"]: "yes" for e in elements}
    marks[elements[0]["id"]] = "no"
    rv = c.put(f"/api/vpoc2/runs/{run_id}/review",
               json={"score": 4, "elements": marks, "goodKo": "분위기 좋음", "badKo": "미소가 약함"})
    assert rv.status_code == 200
    review = rv.get_json()["run"]["review"]
    assert review["reflectionRate"] == round((len(elements) - 1) / len(elements), 3)
    summary = c.get("/api/vpoc2/reviews").get_json()
    assert summary["count"] == 1 and summary["avgScore"] == 4


def test_hq_monthly_limit(client):
    from vpoc2 import ledger

    ledger.reserve_hq("dev", "rA")
    ledger.reserve_hq("dev", "rA")  # 같은 작업은 한 번으로 센다
    with pytest.raises(Exception) as exc:
        ledger.reserve_hq("dev", "rB")
    assert getattr(exc.value, "type", "") == "HqMonthlyLimit"
    meta = client.get("/api/vpoc2/meta").get_json()
    assert meta["hq"]["remaining"] == 0


def test_edit_input_marks_later_steps_stale(client):
    c = client
    run_id = c.post("/api/vpoc2/runs", json={"command": "고양이가 창가에서 졸다가 깬다"}).get_json()["run"]["id"]
    c.post(f"/api/vpoc2/runs/{run_id}/run/interpret")
    wait_task(c, run_id)
    c.put(f"/api/vpoc2/runs/{run_id}/input", json={"command": "고양이가 창가에서 졸다가 기지개를 켠다"})
    run = c.get(f"/api/vpoc2/runs/{run_id}").get_json()["run"]
    assert run["interpretation"]["status"] == "stale" and run["step"] == 1


def test_compose_rules():
    from vpoc2 import compose

    chars = [{"nameKo": "서원", "nameEn": "Seo Won"}]
    assert compose.check_text("beatsEn", "Seo Won turns around", chars)
    assert not compose.check_text("beatsEn", "The racer won the race and turns around", chars)
    assert compose.check_text("beatsEn", "She does not smile", chars)
    assert compose.check_text("beatsEn", "그녀가 웃는다", chars)
    long = "x" * 1300
    assert compose.check_prompt(long, chars)


def test_client_token():
    from vpoc2 import video

    t = video.client_token("r20260930_ab", "s1", 2)
    import re

    assert re.fullmatch(r"[a-zA-Z0-9](-*[a-zA-Z0-9])*", t)
    assert t == video.client_token("r20260930_ab", "s1", 2)


def test_access_denied_on_missing_key_creates_default(tmp_path):
    """주 버킷에 ListBucket 이 없으면 없는 키도 AccessDenied 다 — 기본값 문서만 If-None-Match 로 만든다."""
    from vpoc2 import store
    from vpoc2.errors import Vpoc2Error

    class NoListStore(store.LocalStore):
        def get_bytes(self, bucket, key):
            got = super().get_bytes(bucket, key)
            if got is None:
                raise store.MaybeMissing(Vpoc2Error("AccessDenied", "Access Denied", where="s3.get_object", http=502))
            return got

    s = NoListStore(str(tmp_path))
    obj, _ = store.get_or_create_json(s, "users/_vpoc2/ledger.json", {"entries": []})
    assert obj == {"entries": []}
    store.update_json(s, "users/_vpoc2/ledger.json", {"entries": []}, lambda o: o["entries"].append(1))
    assert store.get_json(s, "users/_vpoc2/ledger.json")[0] == {"entries": [1]}
    # 기본값이 없는 문서(작업 상태)는 삼키지 않고 원래 오류를 올린다
    with pytest.raises(Vpoc2Error) as exc:
        store.get_json(s, "users/dev/video/_vpoc2/rX/run.json")
    assert exc.value.type == "AccessDenied"
