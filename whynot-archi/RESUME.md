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

## 대기 중

| # | 항목 | 누가 |
|---|---|---|
| 1 | 실행 위치 · 저장 위치 · 로그인 (`docs/spec-v1.md` 7장 Q1~Q3) | 설계자 |

## 다음 단계

Q1~Q3 답을 받으면 `docs/spec-v1.md` 6장 조각 K0 부터 만든다. 각 조각은 목 모드로 이 세션에서 확인하고, 실제 AWS 호출 테스트는 설계자가 한다.
