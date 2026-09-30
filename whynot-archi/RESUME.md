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

- vpoc2 코드 v1: `AI-POC-whynot/app/src/vpoc2/` · `frontend/public/vpoc2.*` (이 저장소 = GitLab 브랜치와 동일)
- 목 모드 검증: `tests/` 6건 · 브라우저 ①~⑤ · 합본 15.00초
- GitLab `awstech/ai` 브랜치 `whynot/vpoc2` (커밋 `9112fc0`) → **MR !208**, 브랜치 파이프라인 #820 **success**
  (check:whynot · check:platform · check:platform:module · check:platform:frontend)
- 로컬 검증: check_vpoc.py 전부 통과 · `/api/vpoc2` 라우트 12개 등록 · render dev/prod 미해결 변수 0
- **main 병합은 세션 권한 검사에 막혀 하지 못했다** → 설계자가 GitLab 에서 [Merge] 또는 권한 허용
- 실제 AWS 호출(모델 · S3 쓰기) 사전 점검도 권한 검사에 막혀 하지 못했다 → dev 에서 처음 확인된다
- dev 현재: `ci-def69090`, `/api/vpoc2/meta` 404 (미배포). 운영 `ci-aeed17ff`, videoGen:false

## 대기 중

| # | 항목 | 누가 |
|---|---|---|
| 1 | MR !208 병합 (https://gitlab.meta-clouds.com/awstech/ai/-/merge_requests/208) | 설계자 |
| 2 | 병합 후 main 파이프라인 · `/api/health` imageTag · `/api/vpoc2/meta` 401 확인 | Claude |
| 3 | dev 에서 실제 테스트 → 리뷰 | 설계자 |

## 다음 단계

병합되면 main 파이프라인(build → deploy:whynot:dev)을 보고, dev `/api/health` 의 imageTag 가 새 `ci-<sha8>` 인지, `/api/vpoc2/meta` 가 401 인지 확인한다. 이후 설계자 테스트 결과를 받아 수정한다.
