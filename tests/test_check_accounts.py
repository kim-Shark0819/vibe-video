"""계정 번호 ↔ 고객 이름 짝 검사. 이 파일의 예시 문자열은 번호와 이름을 다른 줄에서 이어 붙여 저장소 검사에 걸리지 않게 한다."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import check_accounts as ca  # noqa: E402

YLAB = "892278727066"
IMAGINUS = "726990466389"
HUB = "730335451955"
FAKE = "1234567" + "89012"


def test_wrong_customer_flagged():
    errs = ca.check_line("이매지너스 운영 계정 " + YLAB)
    assert len(errs) == 1 and "ylab" in errs[0]


def test_right_customer_ok():
    assert ca.check_line("이매지너스 운영 계정 " + IMAGINUS) == []
    assert ca.check_line("| 와이랩 운영 | `" + YLAB + "` |") == []


def test_hub_with_customer_ok():
    assert ca.check_line("dev-keyeast (통합계정 " + HUB + ")") == []


def test_line_naming_both_ok():
    assert ca.check_line("이매지너스로 적힌 " + YLAB + " 은 와이랩 번호다") == []


def test_ignore_marker():
    assert ca.check_line("이매지너스 " + YLAB + " <!-- account-check: ignore -->") == []


def test_unknown_account_in_slot():
    assert ca.check_line("arn:aws:iam::" + FAKE + ":role/x")
    assert ca.check_line('account: "' + FAKE + '"')
    assert ca.check_line("값 " + FAKE + " 은 계정이 아니다") == []


def test_tenant_file_mismatch():
    text = "tenant: whynot\nenv: prod\naccount: \"" + YLAB + "\"\n"
    errs = ca.check_text(text, "tenants/whynot/prod.yaml")
    assert len(errs) == 1 and "tenant: whynot" in errs[0]
    assert ca.check_text(text.replace(YLAB, HUB), "tenants/whynot/dev.yaml") == []


def test_repo_clean(capsys):
    assert ca.main([ROOT]) == 0
