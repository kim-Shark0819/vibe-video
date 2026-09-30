# 와이낫 영상 품질 개선 — 재개 지점 (2026-09-30)

다른 도구 · 다른 세션이 이어받을 때 이 파일부터 읽는다.

## 역할과 저장소

- 설계자(사용자)가 결정 · 승인, 개발자(AI)가 설계 · 코드 작성.
- **이 GitHub 저장소(`kim-Shark0819/vibe-video`)는 보관용이다.** 실제 코드 · 배포는 사내 GitLab `awstech/ai` (`AI-POC-whynot/`) 에서 한다.
- 모든 답변은 한국어. 자격증명 · 키 값은 출력 · 기록 · 커밋하지 않는다.

## 읽는 순서

1. `whynot-archi/와이낫 인수인계 (클라우드 세션용).md`
2. `whynot-archi/AI-POC-whynot/CLAUDE.md`
3. `whynot-archi/AI-POC-whynot/docs/vpoc1/PRD.md` · `steps.md` · `phase2-handoff.md`
4. **`whynot-archi/plans/prompt-quality-plan.md` (현재 작업 계획 v2)**

## 지금 목표

와이낫 영상(Luma Ray2 via Bedrock)의 품질 개선. 첫 과제는 사용자의 짧은 문장을 영상용 세부 프롬프트로 바꾸는 **연출 단계** 추가 (계획서 2장).

## 결정된 것 (2026-09-30)

| 항목 | 결정 |
|---|---|
| 테스트 해상도 | 540p 고정 (설계자 지시는 480p 였으나 Bedrock Luma Ray2 는 540p · 720p 만 지원 — 설계자 확인 대기) |
| 720p | 월 1회 최종 결과 확인용만. 서버가 강제 |
| 실험 예산 | 승인 (540p 약 86.5 USD + 720p 월 최대 45 USD) |

## 대기 중

| # | 항목 | 누가 |
|---|---|---|
| 1 | 코드 zip (`AI-POC-whynot/app/src/vpoc/` 등 — 목록은 계획서 대화 기록 / 아래) + 기준 커밋 sha | 설계자 |
| 2 | 현재 결과 샘플: 완료 계획 1~2개의 `state.json` · `jobs/*.json` · `final.json` + MP4 2~3개 (영상은 약 2주 뒤 만료) | 설계자 |
| 3 | 품질 비교 대상과 가장 큰 증상 (흐림 · 움직임 · 지시 불이행 · 얼굴) | 설계자 |
| 4 | 샷 첫 장면 이미지(L3) 확대 승인 여부 | 설계자 |
| 5 | 480p → 540p 대체 확인 | 설계자 |

코드 zip 목록: `app/src/vpoc/` 전체 · `frontend/public/vpoc.js` · `vpoc.css` · `tools/check_vpoc.py` · `tools/vpoc_e2e.py` · `deploy/config.env.example` · `deploy/config.prod.env` · `k8s/workloads.yaml.tmpl` · `app/requirements.txt` · `docs/vpoc1/` · `docs/구조분석.md` (모두 `AI-POC-whynot/` 아래, `git archive origin/main` 로 묶는다).

## 다음 단계

zip 이 오면 계획서 S0(코드 확인 → 계획 v3) → S2(연출 단계 구현, 스위치 `VPOC_DIRECTOR_ENABLED`) 순서. 코드 결과물은 이 저장소에 패치로 올리고, 적용 · 배포 · 실측은 GitLab 쪽 로컬 세션이 한다.
