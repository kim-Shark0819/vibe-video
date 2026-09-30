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

- vpoc2 코드 v1 작성 완료: `AI-POC-whynot/app/src/vpoc2/` · `frontend/public/vpoc2.*`
- 목 모드 검증: `tests/` 5건 통과 · 브라우저(Playwright) ①~⑤ 흐름 통과 · 합본 15.00초 확인 · 모바일 가로 넘침 없음
- 실제 AWS 호출은 아직 한 번도 하지 않았다 (이 세션은 AWS 에 닿지 않는다)

## 대기 중

| # | 항목 | 누가 |
|---|---|---|
| 1 | `docs/integration.md` 대로 awstech/ai 에 적용 → dev 배포 | 로컬 세션 (GitLab push 가능한 곳) |
| 2 | dev 에서 실제 테스트 → 리뷰 남기기 | 설계자 |

## 다음 단계

설계자 테스트 결과(오류 원문 · 리뷰의 아쉬운 점)를 받아 수정한다. 리뷰가 쌓이면 spec 3-3 v2(아쉬운 점을 연출 지시문 주의사항으로) 진행.
