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

## 방향 전환 (2026-09-30)

기존 vpoc1 코드를 받지 않고 **이 저장소에서 새로 만든다(vibe 코딩).** 정본 명세는 **`docs/spec-v1.md`**.
`whynot-archi/plans/prompt-quality-plan.md` 는 연출 단계 설계(2장)만 참고로 쓴다 — 실험 · 시험 세트 · 코드 zip 부분은 폐기.

핵심: 명령 → AI 해석(명령 요소 체크리스트) → 캐릭터 이미지 확정 → 15초(5초 × 3샷) 540p 영상 → 사용자 리뷰(점수 · 요소별 반영 · 좋은 점 · 아쉬운 점).

## 현재 상태 (2026-09-30)

- **vpoc2 dev 배포 완료.** MR !208 병합(설계자) → main `0e07c2e9` → 파이프라인 #822 success → dev imageTag `ci-0e07c2e9` (병합 후 약 2분 반)
- dev 확인: `/api/vpoc2/meta` · `/api/vpoc2/runs` 401(등록됨, 인증 먼저) · vpoc1 `/api/vpoc/p/x` 401 그대로 · `vpoc2.js` 배포본 = 이 저장소 파일 · 브라우저 로드 오류 0
- 운영(`whynot`)은 변경 없음 (`VPOC2_ENABLED=false`, `videoGen:false`)
- 실제 AWS 모델 호출은 아직 한 번도 안 됐다 — 설계자 첫 테스트가 첫 호출이다
- 이 저장소 코드 = GitLab main 의 `AI-POC-whynot/app/src/vpoc2/` · `frontend/public/vpoc2.*`

## 2026-10-02 변경 — dev 테스트가 막혔다

- 방침: **통합계정(730335451955)에 AI POC 과금 0.** 개발을 각 고객사 계정으로 옮긴다(Kiro 진행, 결정 대기). 검토 문서 `docs/dev-migration-review.md`
- Kiro 실측(10-02): ns `whynot` 0/0, `dev-whynot.meta-clouds.com/api/health` 503. 9-30 이후 누가 내렸는지는 확인 필요
- dev-whynot 에서 테스트하면 모델 호출(Luma Ray2 · SD3.5 · Claude)이 통합계정에 과금된다
- **결정(10-02, 지시 D-G):** vpoc2 테스트는 와이낫 계정 dev(이관 파일럿)에서 한다. 통합계정 dev-whynot 은 다시 켜지 않는다(F-1 신규 생성 중지). 아래 1번은 와이낫 계정 dev 가 생기면 주소만 바꿔 진행

## 대기 중

| # | 항목 | 누가 |
|---|---|---|
| 0 | 와이낫 계정 dev 구축(Kiro 이관 1단계 파일럿 — dev 만, 운영 그대로. `docs/kiro-command-dev-only.md`) | Kiro |
| 1 | dev 테스트: 메인에서 로그인한 **같은 탭**에서 `https://dev.whynot.meta-clouds.com/vpoc2.html` → ①~⑤ → 리뷰 (예전 주소 `dev-whynot.meta-clouds.com` 은 통합계정이라 쓰지 않는다) | 설계자 |
| 2 | 오류가 나면 화면의 오류 원문(where · type · message · requestId) 전달 | 설계자 |

## 다음 단계

테스트 결과로 수정한다. 수정은 이 저장소에서 하고 GitLab 브랜치 → MR → (설계자 병합) → dev. vpoc2.js · css 를 바꾸면 vpoc2.html 의 `?v=` 를 올린다.
