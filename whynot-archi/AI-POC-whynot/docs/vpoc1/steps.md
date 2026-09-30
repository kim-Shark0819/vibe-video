# vpoc1 실행 순서

정본 설계는 `PRD.md` 다. 이 파일은 실행 순서와 게이트만 정한다.

## 이번 실행(2026-09-23)에서 한 것

| 단계 | 내용 | 결과 |
|---|---|---|
| 1 | 백업 태그 · 작업 트리 · 전체 검토 | `backup/whynot-video-v4-20260923` → `d62d020` 원격 push. worktree `whynot/vpoc1`. `review.md` |
| 2 | 사전 점검 Gate 0 (C1~C10, Luma 실호출 1건) | **통과.** 3.83 USD. `preflight-20260923T0630Z.json` · `run-log.md` |
| 3 | 구 영상 기능 제거 · CI 교체 · 문맥 정리 · 진입점 | `server.py` 5,473줄 제거, 모듈 28개+디렉터리 5개, 프론트 8개, 검사기 36개, spec 10개 삭제. CI → `check_vpoc.py` 하나 |
| 4 | 영상 경로 + 테스트 페이지 | `vpoc/video.py` `ledger.py` `store.py` `compose.py` `errors.py` `settings.py`, `/api/vpoc/smoke`, `vpoc-smoke.html`+`.js`, 설정 18키, CSP |
| 5 | 나머지 백엔드 | `routes.py`(라우트 8개) `llm.py`(부록 D) `images.py`. 작업 스레드·stale·되돌리기·generate/retry·완료 처리·Neptune 속성 5개 |
| 6 | 프론트엔드 | `vpoc.js`(4단계 화면 + 프로젝트 보기 + 픽스처) `vpoc.css` |
| 7 | 병합 · 배포 | 아래 게이트 참고 |

## 게이트

| 게이트 | 판정 기준 | 누가 |
|---|---|---|
| **Gate 0** | 부록 C 의 P0 항목 전부 ok | 자동 (`vpoc_preflight.py`) — **통과** |
| **Gate 1** | `vpoc-smoke.html` 에서 영상이 브라우저에 재생된다 (3.75 USD) | **사용자** — 대기 |
| **Gate 2** | F1 예시 4샷이 전부 completed 이고 presigned GET 이 200/206, 재생된다 (약 15.2 USD) | 사용자 또는 `vpoc_e2e.py` — 대기 |
| **Gate 3** | 부록 E 체크리스트 1~10 | **사용자** — 대기 |

## 공통 규칙

- 사용자에게 기술 판단을 묻지 않는다. 막히면 `PRD.md` 10장대로 처리하고 `run-log.md` 에 적는다.
  멈춰서 묻는 것은 E3 최종 실패뿐이다(E19 비용 상한은 2026-09-23 에 없앴다).
- 한 문제에 20분이 넘으면 10장대로 처리하고 진행한다.
- 금지: 백업 태그 checkout·diff·참조 / 다른 고객 디렉터리와 그 CI job·Kiro 파일 수정 /
  `kubectl apply`·`edit`·`set`·`scale`·`delete`(조회만) / Terraform 실행 / D-L02 밖 인프라 변경 /
  S3·Neptune 데이터 삭제 / `docs/vendor` 삭제 / prod 배포.
- 환경: AWS 계정 `730335451955`, 워크스테이션 `aws` 명령에 `--profile ai-poc-hub`(파드 안에서는
  붙이지 않는다 — IRSA), 네임스페이스 `whynot`, dev `https://dev-whynot.meta-clouds.com/`
