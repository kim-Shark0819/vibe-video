"""계정 번호와 고객 이름의 짝을 검사한다. 고객 계정 번호가 다른 고객 이름 옆에 적히면 실패한다.

    python tools/check_accounts.py [경로 ...]     # 기본: 저장소 루트 전체

사고: PRD 에 이매지너스 계정을 와이랩 번호(892278727066)로 적었다 (2026-10-02 발견).
정본은 CLAUDE.md §1 계정 표다. 그 표를 바꾸면 아래 ACCOUNTS 도 같이 바꾼다.

검사:
  1. 한 줄에 고객 이름이 있고, 그 줄의 고객 계정 번호 주인이 그 이름들 중에 없으면 실패
  2. tenants/*.yaml 처럼 `tenant: <고객>` 이 있는 파일에 다른 고객의 계정 번호가 있으면 실패
  3. 계정 자리(ARN 계정 칸, account 값, "계정" 뒤)에 대장에 없는 번호가 있으면 실패
한계: 한 줄에 여러 고객과 여러 번호가 섞이면 짝이 뒤바뀐 것은 못 잡는다.
일부러 다른 고객 번호를 적어야 하는 줄에는 `account-check: ignore` 를 붙인다.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 통합계정(허브)에는 모든 고객의 개발계가 있어서 고객 이름과 같이 적혀도 정상이다.
HUB = "730335451955"
ACCOUNTS = {
    "089540175779": "whynot",
    "722500516860": "keyeast",
    "892278727066": "ylab",
    "726990466389": "imaginus",
}
ALIASES = {
    "whynot": ("와이낫", "whynot"),
    "keyeast": ("키이스트", "keyeast"),
    "ylab": ("와이랩", "ylab"),
    "imaginus": ("이매지너스", "imaginus", "story-ai"),
}
KNOWN = set(ACCOUNTS) | {HUB}

ID_RE = re.compile(r"(?<![0-9])[0-9]{12}(?![0-9])")
SLOT_RE = re.compile(
    r"arn:aws[\w-]*:[\w-]*:[\w-]*:([0-9]{12}):"
    r"|account\W{0,4}([0-9]{12})(?![0-9])"
    r"|계정\W{0,4}([0-9]{12})(?![0-9])",
    re.IGNORECASE,
)
TENANT_RE = re.compile(r"^tenant:\s*([\w-]+)", re.MULTILINE)
IGNORE = "account-check: ignore"
TEXT_EXT = (".md", ".yaml", ".yml", ".json", ".txt", ".py", ".ps1", ".sh", ".tf", ".env", ".example", ".js", ".html")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".vpoc2-local"}


def named(line: str) -> set[str]:
    low = line.lower()
    return {c for c, names in ALIASES.items() if any(n.lower() in low for n in names)}


def check_line(line: str, tenant: str | None = None) -> list[str]:
    if IGNORE in line:
        return []
    errs = []
    names = named(line)
    for m in ID_RE.finditer(line):
        acc = m.group(0)
        owner = ACCOUNTS.get(acc)
        if not owner:
            continue
        if names and owner not in names:
            errs.append(f"{acc} 는 {owner} 계정인데 이 줄은 {', '.join(sorted(names))} 를 말한다")
        elif tenant and owner != tenant:
            errs.append(f"{acc} 는 {owner} 계정인데 이 파일은 tenant: {tenant} 다")
    for m in SLOT_RE.finditer(line):
        acc = next(g for g in m.groups() if g)
        if acc not in KNOWN:
            errs.append(f"{acc} 는 계정 대장(CLAUDE.md §1)에 없는 번호다")
    return errs


def check_text(text: str, path: str = "") -> list[str]:
    tenant = None
    if path.endswith((".yaml", ".yml")):
        m = TENANT_RE.search(text)
        if m and m.group(1) in ALIASES:
            tenant = m.group(1)
    out = []
    for no, line in enumerate(text.splitlines(), 1):
        out.extend(f"{path}:{no}: {e}" for e in check_line(line, tenant))
    return out


def iter_files(paths: list[str]):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for d, dirs, files in os.walk(p):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
            for f in sorted(files):
                if f.endswith(TEXT_EXT):
                    yield os.path.join(d, f)


def main(argv: list[str]) -> int:
    paths = argv or [ROOT]
    errs, count = [], 0
    for f in iter_files(paths):
        with open(f, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        count += 1
        errs.extend(check_text(text, os.path.relpath(f, ROOT)))
    for e in errs:
        print(e)
    print(f"check_accounts: 파일 {count} · 문제 {len(errs)}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
