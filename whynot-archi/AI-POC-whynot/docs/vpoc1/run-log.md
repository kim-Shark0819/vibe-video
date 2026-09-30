# vpoc1 실행 기록

작업 트리 `C:\dev\ai\.worktrees\vpoc1` · 브랜치 `whynot/vpoc1` · 2026-09-23

---

## Gate 0 — 사전 점검

원본 결과: `docs/vpoc1/preflight-20260923T0630Z.json` (무료 항목만 돌린 첫 판은 `preflight-free.json`)

| id | 등급 | 결과 | 실측 |
|---|---|---|---|
| C1 | P0 | ok | `luma.ray-v2:0` ACTIVE · us-west-2 · ON_DEMAND · 출력 VIDEO |
| C2 | P0 | ok | `stability.sd3-5-large-v1:0` ACTIVE · us-west-2 |
| C3 | P0 | ok | Claude Sonnet 4.5 (`global.` 프로필) Converse ping 1,641ms · in 8 / out 5 토큰 |
| C4 | P0 | ok | 앱 역할 `arn:aws:iam::730335451955:role/whynot-app-role`, web identity 신뢰 확인. EKS 엔드포인트가 사설이라 SA annotation 조회는 못 하고 IAM 에서 확인했다 |
| C5 | P0 | ok (조치 후) | 10개 검사 중 `s3:ListBucket`(영상 버킷) 하나가 implicitDeny → 인라인 정책 `vpoc1-luma` 추가 후 전부 allowed. `infra-changes.md` 참고 |
| C6 | P0 | ok | `whynot-video-730335451955-us-west-2` 이 **이미 있다**(us-west-2). 새로 만들지 않았다 |
| C7 | P0 | ok | 주 버킷 `whynot-730335451955` 에 `users/_vpoc1/preflight.txt` 1,061바이트 쓰기·읽기 |
| C8 | P1 | ok | **`On-demand model inference concurrent requests for Luma Ray V2` = 1.0** → `VPOC_MAX_INFLIGHT=1` |
| C9 | P0 | ok | SD3.5 1장 · `finish_reasons=[None]` · seed 1837461 · 0.08 USD |
| C10 | P0 | ok (검사 방식 보정 후) | 아래 표 |

### C10 — Luma Ray2 실호출 1건

| 항목 | 값 |
|---|---|
| invocationArn | `arn:aws:bedrock:us-west-2:730335451955:async-invoke/r08qxkzwif7l` |
| clientRequestToken | `preflight-20260922T212442Z` |
| 프롬프트 | PRD 6.5 형식 영어 **1,108자** (조립 상한 1,200자 안) |
| 파라미터 | 텍스트 전용 · `5s` · `540p` · `16:9` · `loop:false` |
| 제출 → Completed | **72초** (PRD 예상 2~5분보다 빠르다) |
| 출력 키 | `users/_vpoc1/preflight/20260922T212442Z/r08qxkzwif7l/output.mp4` |
| 크기 | 1,164,649 바이트 (1.16MB) |
| Content-Type | `application/octet-stream` — presign 에서 `video/mp4` 로 덮는다 |
| presigned GET | `206 Partial Content`, `Content-Range: bytes 0-0/1164649` |
| 비용 | 3.75 USD |

첫 판정은 **실패로 나왔다.** presigned URL 에 HEAD 를 보냈기 때문이다 — SigV4 presigned URL 은
메서드에 묶여 있어서 `get_object` 로 서명한 URL 에 HEAD 를 보내면 403 이다. 검사기를
GET + `Range: bytes=0-0` 으로 바꿔 재확인했다(무료). 영상과 권한 자체는 처음부터 정상이었다.

**Gate 0 통과.** P0 전부 ok.

### 사용 금액

| 항목 | 금액 |
|---|---|
| C9 SD3.5 1장 | 0.08 USD |
| C10 Luma 1건 | 3.75 USD |
| **합계** | **3.83 USD** (상한 60 USD) |

`ledger.seed_from_preflight(3.83)` 로 원장 첫 항목에 넣는다(키 `gate0-preflight-20260923`).

---

## 구 기능 제거

| 항목 | 수치 |
|---|---|
| `server.py` | 12,253줄 → 6,780줄 (**5,473줄 제거**, 영상 라우트 61개 + 헬퍼 42개) |
| 삭제한 백엔드 모듈 | 파일 28개 + 디렉터리 5개(`story_video/` `scene_video/` `roles/video/` `fixtures/video/` `tests/`) |
| 삭제한 프론트 스크립트 | 8개 (`story-app.js` 181KB 포함) |
| 삭제한 검사기·도구 | 36개 |
| 삭제한 spec · steering | 10개 디렉터리 + 3개 파일 |
| 삭제한 문서 | 파일 20개 + 경로 7개 |
| 잔존 | 7건 (`review.md` 2-b 에 사유 기록) |

제거 방법: `ast` 로 `server.py` 최상위 노드 경계를 잡고 (1) 영상 라우트 (2) 삭제된 이름을
참조하는 최상위 정의를 고정점까지 반복 제거했다. 라우트 함수 이름은 전파 대상에서 뺐다 —
`videos` 같은 흔한 이름이 무관한 지역 변수와 부딪혀 플랫폼 라우트(`patch_model`, `dashboard`)를
끌고 갔기 때문이다. import 문은 이름 단위로 따로 손봤다(통째로 지우면 플랫폼 모듈도 사라진다).

`project_tracks.install(...)` 이 `video_store` 참조 때문에 함께 쓸려 나가 복원했다. 트랙 선택은
플랫폼 기능이다.

---

## 검사 결과 (로컬)

```
python -X utf8 AI-POC-whynot/tools/check_vpoc.py
[ok  ] compileall app/src
[ok  ] 앱 임포트 스모크 — routes 71
[ok  ] node --check (4 files)
[ok  ] 잔존 검사 — 구 식별자 45종 0건
[ok  ] 조립기 자체 검사 7건
전부 통과
```

등록된 vpoc 라우트 8개:

```
GET    /api/vpoc/p/<pid>
POST   /api/vpoc/p/<pid>/plans
GET    /api/vpoc/p/<pid>/plans/<plan_id>
POST   /api/vpoc/p/<pid>/uploads
PUT    /api/vpoc/p/<pid>/plans/<plan_id>/steps/<int:number>
POST   /api/vpoc/p/<pid>/plans/<plan_id>/run/<action>
POST   /api/vpoc/p/<pid>/plans/<plan_id>/back
POST   /api/vpoc/smoke  ·  GET /api/vpoc/smoke/<smoke_id>
```

렌더 확인 (미해결 `${VAR}` 0건):

```
python AI-POC-whynot/deploy/render.py              -> 템플릿 18개 (dev)
python AI-POC-whynot/deploy/render.py --target prod -> 템플릿 18개 (prod)
```

---

## 남은 확인 — 사용자 브라우저에서

정적 검사 통과는 완료 증거가 아니다(R3). 아래는 **사람이 브라우저에서** 확인해야 한다.

| # | 확인 | 방법 |
|---|---|---|
| Gate 1 | 영상 1건이 재생된다 (3.75 USD) | `https://dev-whynot.meta-clouds.com/vpoc-smoke.html` → [테스트 영상 만들기] |
| Gate 1b | AWS 오류 원문이 화면에 그대로 보인다 (과금 없음) | 같은 페이지 → [AWS 오류 원문 시험] |
| Gate 2·3 | F1 예시 4샷 (약 15.2 USD) | PRD 부록 E 체크리스트 |

Gate 2 의 E2E 를 자동으로 돌리려면 dev 로그인 계정(`VPOC_E2E_USER`·`VPOC_E2E_PASS`) 또는
앱 파드 exec 이 필요하다. 이 작업에서는 둘 다 없었다 — EKS API 엔드포인트가 사설이라
워크스테이션에서 `kubectl exec` 가 되지 않는다(`dial tcp 100.10.6.238:443: i/o timeout`).

### 샷별 기록 표 (E2E 실행 후 채운다)

| 샷 | invocationArn | 모드 | 제출 | 완료 | 소요 | 프롬프트 길이 | 비용 | 오류 원문 |
|---|---|---|---|---|---|---|---|---|
| s1 | | | | | | | | |
| s2 | | | | | | | | |
| s3 | | | | | | | | |
| s4 | | | | | | | | |

---

## 병합과 배포 (2026-09-23)

| 시각 (UTC) | 일 | 결과 |
|---|---|---|
| 22:28 | `git push -u origin whynot/vpoc1` | 파이프라인 511 |
| 22:29 | 파이프라인 511 `check:whynot` | **success · 34초** (CI 1회 소요 = 34초, 30분 규칙 S3 미발동) |
| 22:30 | MR !124 생성 → main 병합 | merge commit `f3c7a1e` |
| 22:30 | 파이프라인 513 (main) | `check:whynot` success · `probe:whynot:images` success · `build:whynot:app` success · `build:whynot:frontend` success · `deploy:whynot:dev` **success** · `deploy:whynot:prod` manual(실행 안 함) |
| 22:39 | ArgoCD `whynot-dev` 동기화 완료 | 반영까지 약 9분 (E23 한도 20분 안) |

이미지 태그 `ci-f3c7a1ed` (CI가 정한다. 손으로 정하지 않았다).

### dev 확인 (HTTP 조회만)

| 확인 | 결과 |
|---|---|
| `GET /api/health` | 200 · `imageTag: ci-f3c7a1ed` · `gitContext: main@f3c7a1ed` · account guard `allowed: true` (`730335451955`) |
| `GET /health` (프론트) | 200 |
| `GET /index.html` | 200. `<div id="vpoc-root">` 있음. script 태그 3개뿐 — `runtime-config.js` `app.js` `vpoc.js`. `__ASSET_VERSION__` 미치환 0건 |
| `GET /vpoc.js` · `/vpoc.css` | 200 (52,767 · 11,656 바이트), `?v=ci-f3c7a1ed` |
| `GET /vpoc-smoke.html` · `/vpoc-smoke.js` | 200 (1,585 · 5,105 바이트). SPA fallback 이 아니라 실제 파일이다 |
| `GET /api/vpoc/p/x` (인증 없이) | **401** — 라우트가 등록됐고 인증이 먼저 걸린다 |
| `GET /api/vpoc/smoke/x` (인증 없이) | **401** |
| `GET /api/videos` | **404** — 구 영상 라우트 제거 확인 |
| `GET /api/scenes` | **404** |
| `GET /api/v2/video/jobs` | **404** |

`kubectl -n whynot get deploy -o wide` 로 이미지 태그를 보려 했으나 EKS API 엔드포인트가
사설이라 워크스테이션에서 되지 않는다. 대신 `/api/health` 의 `imageTag`·`gitContext` 로 확인했다.

### platform-drift job

파이프라인 513 에서 `platform-drift` 가 failed 다. **이 job 은 `allow_failure` 라 파이프라인은
success 이고, 내 변경 전 main(`d62d020`, 파이프라인 509)에서도 이미 failed 였다** — 기존 상태다.

내용은 경고다: "플랫폼 파일 17개가 디렉터리 간에 다르다. 의도한 것인지 확인하고, 공통 수정이면
AI-POC/ 에서 먼저 고친 뒤 옮긴다." 이번 변경으로 다음 플랫폼 파일의 drift 가 늘었다 —
`gateway.py`(주석) · `model_registry.py` · `providers.py` · `frontend/Dockerfile` ·
`frontend/nginx.conf` · `k8s/model-catalog.yaml.tmpl`. 전부 **whynot 전용 영상 카탈로그·CSP·치환
대상** 변경이고 다른 고객에 옮길 내용이 아니다. 다른 고객 디렉터리와 그 CI job 은 건드리지 않았다.

### 아직 남은 것 (사람이 브라우저에서)

| 게이트 | 확인 | 비용 |
|---|---|---|
| Gate 1 | `https://dev-whynot.meta-clouds.com/vpoc-smoke.html` → [테스트 영상 만들기] → 2~5분 뒤 재생 | 3.75 USD |
| Gate 1b | 같은 페이지 → [AWS 오류 원문 시험] → AWS 원문 오류 | 0 |
| Gate 2 | F1 예시 4샷 (`tools/vpoc_e2e.py` 또는 브라우저) | 약 15.2 USD |
| Gate 3 | `PRD.md` 부록 E 체크리스트 1~10 | Gate 2 에 포함 |

원장 누계: **3.83 USD** / 상한 60 USD (Gate 0 사전 점검만 반영. 앱이 처음 뜰 때
`ledger.seed_from_preflight(3.83)` 이 키 `gate0-preflight-20260923` 으로 한 번 넣는다).

---

## 결함 1 — clientRequestToken 에 밑줄 (2026-09-23, Gate 1/2 중)

### 증상

dev 에서 F1 이 아닌 다른 입력(검정 고양이)으로 ③까지 정상 진행한 뒤 승인했는데 **4샷 전부**
제출 단계에서 실패했다. 화면에 AWS 원문이 그대로 보였다(설계대로 동작한 부분이다).

```
✖ luma.start_async_invoke · ValidationException
1 validation error detected: Value 'pl_20260922_de38-shot_01-1' at 'clientRequestToken'
failed to satisfy constraint: Member must satisfy regular expression pattern:
[a-zA-Z0-9](-*[a-zA-Z0-9])*
HTTP 400  requestId 8861c113-3720-4a06-a748-a8f40d8b387d  at 2026-09-22T22:59:58Z
```

### 원인

`clientRequestToken` 은 **`[a-zA-Z0-9](-*[a-zA-Z0-9])*` 를 만족해야 한다. 밑줄을 받지 않는다.**
PRD 5.1 이 AWS 문서를 "1~256자, 인쇄 가능 ASCII" 로 적어 두었고 나는 그것을 그대로 믿었다.
우리 `planId`(`pl_20260922_de38`)와 `shotId`(`shot_01`)는 밑줄을 쓴다.

Gate 0 C10 이 이것을 잡지 못한 이유: 사전 점검은 토큰을 `preflight-<UTC시각>` 으로 직접 만들어
써서 밑줄이 없었다. **실제 코드 경로(`video.client_token`)를 쓰지 않은 것이 검사의 구멍이었다.**

### 과금

없다. ValidationException 은 API 검증 계층에서 나고 비동기 작업이 만들어지지 않는다 —
22:59:58 의 4건 실패 뒤 `ListAsyncInvokes` 에 작업이 하나도 남지 않은 것으로 확인했다.
`submit_shot` 은 제출이 성공한 뒤에만 `ledger.charge_video` 를 부른다.

### 고침

`video.client_token()` 이 영숫자가 아닌 것을 `-` 로 바꾸고 앞뒤 `-` 를 떼고 256자로 자른다.
`pl_20260922_de38` + `shot_01` + attempt 1 → `pl-20260922-de38-shot-01-1`.
같은 (planId, shotId, attempt) 는 항상 같은 값이라 멱등성이 유지된다.

`check_vpoc.py` 에 멱등 키 검사 5건을 넣었다 — 실제 `video.client_token` 을 불러 AWS 패턴과
대조하고, 밑줄·길이·멱등성·충돌을 본다. 같은 결함이 다시 나면 CI 에서 걸린다.

### 실제 API 로 검증

새 형식을 실호출로 확인했다.

| 항목 | 값 |
|---|---|
| 토큰 | `pl-20260922-de38-shot-01-9` — **수락됨** (ValidationException 없음) |
| invocationArn | `arn:aws:bedrock:us-west-2:730335451955:async-invoke/mm0oexhd8y31` |
| 상태 | `Failed` · `failureMessage: prompt is required` |
| 소요 | 제출 23:03:14 → 종료 23:03:15 (**1초**), 출력 없음 |

## 결함 2 — 빈 프롬프트는 거절되지 않는다 (같은 확인에서 발견)

위 검증은 "빈 프롬프트를 보내면 AWS 가 검증 오류를 내므로 과금 없이 토큰만 확인할 수 있다"는
전제로 했다. **그 전제가 틀렸다.** 빈 프롬프트는 API 검증을 통과해 비동기 작업으로 들어가고
1초 뒤 `prompt is required` 로 Failed 가 된다.

영향 두 가지.

1. **테스트 페이지의 오류 시험 버튼.** PRD 부록 E 9 와 7.1 은 "빈 프롬프트를 그대로 보내
   원문 오류를 확인한다(과금 없음)" 이었다. 과금 없음이 보장되지 않는다. 버튼을
   **[AWS 오류 원문 시험 (과금 없음)]** 으로 바꾸고, 일부러 패턴을 어기는 멱등 키를 보내
   API 검증 계층에서 거절당하게 했다(`video.error_probe`). 작업이 만들어지지 않아 과금이 없다.
   서버는 `POST /api/vpoc/smoke {"errorTest": true}` 로 받는다.
2. **앱 경로는 원래 안전했다.** `video.submit` 이 빈 프롬프트를 로컬에서 먼저 막는다. 그 가드를
   지우면 과금이 새므로 주석에 근거(arn `mm0oexhd8y31`)를 적어 두었다. `smoke_start` 가 빈
   프롬프트일 때 원장 상한 검사를 건너뛰던 것도 고쳤다.

### 원장 반영

`mm0oexhd8y31` 은 출력이 없는 Failed 작업이다. Luma 단가는 **출력 초당** 이라 AWS 실제 청구는
0일 가능성이 높지만 여기서 확인할 방법이 없고, 원장은 실패 작업도 보수적으로 계상한다(PRD 6.6).

| 원장 항목 | 금액 | 내용 |
|---|---|---|
| `gate0-preflight-20260923` | 3.83 | Gate 0 — SD3.5 1장 + Luma 1건(완료, 출력 1.16MB) |
| `tokencheck-20260923` | 3.75 | 토큰 형식 실검증 — Failed 1초, 출력 없음 |
| **누계** | **7.58** | / 상한 60 USD |

두 항목은 앱이 처음 뜰 때 `ledger.seed()` 가 멱등하게 넣는다.
