# CLAUDE.md — AI POC 프로젝트 인수인계 (Kiro → Claude Code)

작성 2026-09-28. 이 파일은 작업 폴더 루트에 둔다. Claude Code 는 시작할 때 이 파일을 자동으로 읽는다.
지금까지 Kiro 로 진행한 작업의 상태·결정·규칙을 담았다. **이 파일과 저장소의 문서가 다르면 저장소 문서가 최신이다** — 특히 `platform/docs/unattended-log.md` 의 마지막 재개 지점을 먼저 확인할 것.

---

## 0. 지금 가장 먼저 할 일

**최우선 목표: 이매지너스 운영(`https://imaginus.meta-clouds.com`)에서 스토리 개발 기능을 쓸 수 있게 한다. 화면은 현재 운영 UI 그대로.**

현재 판단 (2026-09-28 Kiro 2단계 결과):

- 운영에 스토리 개발 7단계(틀·기획방향·인물·시놉시스·트리트먼트·마무리·대본)가 **이미 배포돼 있다.** 라우트 `/api/story/*` 가 401 을 준다(로그인 필요 = 라우트 존재).
- 노출 조건 = 서버 env `STORY_DEV_ENABLED`(운영값 `"true"`, 렌더된 매니페스트에서 확인) **AND** 계정의 `beta` 역할.
- `beta` 기본 부여 변경은 `ON CREATE SET` 에만 붙어 **기존 계정에는 `beta` 가 없다.** 사용자가 운영에서 스토리 개발을 못 본 이유로 가장 유력하다.

다음 순서:

1. **사용자가 운영 관리자 화면에서 자기 계정에 `beta` 역할을 부여해 확인한다** (결과 대기 중)
2. 풀리면 → 배포 불필요. 다음은 캐릭터 검색(§6)
3. 안 풀리면 → `dev-imaginus.meta-clouds.com` 에 **운영과 같은 앱**을 올려(새 플랫폼 셸이 아님) 원인을 재현·수정 → 운영 배포 절차·되돌리기 문서화 → 사용자 승인 후 운영 배포

남은 정리 두 건:

- **`a585a39` 에 remote 가 없다.** 운영과 바이트 동일한 소스(워크스페이스 `이매지너스/` 작업 트리)의 유일한 커밋이 이 PC 에만 있다. 보관 방법 결정 필요(원격 신설 vs `ai` 저장소 사본을 정본으로 맞추기).
- **README 경고 커밋 `75447b6` 이 main 이 아니라 `feat/whynot-video-only` 브랜치에 올라갔다.** main 기준 새 브랜치로 옮길지 결정 필요. 그 체크아웃에는 다른 사람의 수정(`AI-POC/app/src/scene_video/*`)이 있으니 섞지 말 것.

---

## 1. 계정·환경

| 구분 | 계정 | 주소 / 비고 |
|---|---|---|
| 허브(통합 개발) | `730335451955` | 공용 EKS `AI-POC-eks`(엔드포인트 비공개), 공용 ALB `platform-dev-alb`, 프로파일 `ai-poc-hub` |
| **이매지너스 운영** | `726990466389` (story-ai) | `imaginus.meta-clouds.com`, ALB `story-ai-758721242`, 이미지 `20260908-v73`, **배스천 빌드 배포**(GitLab CI 아님). 프로파일 `imaginus-prod` 은 아직 로컬에 없음 |
| 키이스트 운영 | `722500516860` | **빈 계정**(기본 VPC 까지 삭제됨). 프로파일 `keyeast-prod`, `keyeast-prod-deploy` |
| 와이낫 운영 | `089540175779` | `whynot.meta-clouds.com`(목표) |
| 와이랩 운영 | `892278727066` | 프로파일 `ylab` |

로컬 AWS 프로파일: `default · rosa-maker · mtp_ksb · ai-poc-hub · ylab · keyeast-prod · keyeast-prod-deploy · goodrich-mgmt`.
**계정 혼용 금지.** 명령 전 `aws sts get-caller-identity --profile <p>` 로 계정을 확인하고 다르면 멈춘다.

### 개발계 호스트 (허브)

| 호스트 | 무엇 | 상태 |
|---|---|---|
| `ai-poc-web.meta-clouds.com` | AI-POC 레거시 앱 | `ci-def69090`, 무변경 유지 |
| `next-ai-poc.meta-clouds.com` | **새 모듈 플랫폼**(셸 + story 모듈)을 ai-poc 개발계 데이터 위에 올린 검증용 | 운영 UI 와 다르다. 운영의 새 버전이 아니다 |
| `keyeast.meta-clouds.com` | 키이스트 레거시 개발계 | 스토리 개발 7단계 + personalization 원본 |
| `dev-whynot.meta-clouds.com` | 와이낫 개발계 | 장면 영상화 |
| `dev-imaginus.meta-clouds.com` | DNS 는 `platform-dev-alb` 를 가리킴, 아직 규칙 없음(404) | §0 3번에서 **운영과 같은 앱**용으로 쓴다 |

---

## 2. 저장소·작업 위치

| 경로 | 무엇 |
|---|---|
| `gitlab.meta-clouds.com/awstech/ai` (로컬 `C:\dev\ai`) | 공용 플랫폼 저장소. 고객 디렉터리 `AI-POC/`·`AI-POC-keyeast/`·`AI-POC-whynot/`·`AI-POC-이매지너스/`·`AI-POC-ylab/`, 새 플랫폼 `platform/`, 테넌트 선언 `tenants/` |
| 워크스페이스 `이매지너스/` | **이매지너스 운영 소스의 정본.** 커밋 `a585a39`. remote 없음 |
| `AI-POC-이매지너스/` (ai 저장소) | **운영보다 뒤처져 있다**(`story_dev.py` 6.6KB 부족 — 회차 분량 함수 4개). 이 디렉터리로 빌드하지 말 것 |
| `AI-POC-keyeast/app/src/story_dev.py` @ `origin/main` `f0dbad9` | 키이스트 스토리 개발 정본 |
| 브랜치 `platform/s4-story` | 모듈화 작업 브랜치 (최근 `9ca3f20`) |
| worktree `C:\dev\ai\.worktrees\video-module-rebuild` | 와이낫 장면 영상화 작업 |
| worktree `C:\dev\ai\.worktrees\keyeast-bootstrap` | 키이스트 작업 |
| `C:\dev\ai-main` | main 체크아웃 (다른 worktree 가 main 을 쓰면 `git push origin <branch>:main` 로 원격만 전진) |

**한 worktree 에 에이전트 세션 하나.** 다른 고객 작업은 다른 worktree·다른 창에서. 과거에 세션이 겹쳐 출력 파일이 덮이고 브랜치가 엉킨 사고가 있었다.

---

## 3. 트랙별 상태

### 3.1 이매지너스 운영 스토리 개발 — **최우선** (§0)

- 1단계(운영 소스 확보) 완료: `이매지너스/.build/toon-20260908-v73.tar.gz` 가 운영 빌드 아카이브. 작업 트리와 164파일 중 159 동일 · 다름 0 · 아카이브에만 5(렌더된 `k8s/*.yaml`). `gitContext 1b0b355+4` 의 `+4` 중 이미지에 들어간 것은 `graph_store.py` 하나(beta 기본값) → `a585a39` 로 보존.
- 2단계(기능 대조) 완료: S1~S7 **같음**. personalization 은 키이스트에만(13함수 + `/prefs*`). 회차 분량 갈래는 운영에만. 전문 `platform/docs/imaginus-prod-source.md`.
- 3~5단계 보류(§0 결과 대기).

### 3.2 모듈화 플랫폼 (`platform/`)

목적: AI 기능(스토리 개발·콘티·영상 등)을 모듈로 만들어 고객사 4곳에 필요한 조합만 배포. 지시서 `platform/docs/kiro-7steps.md`.

| 단계 | 상태 |
|---|---|
| 1 기준선 확정 | 완료 |
| 2 계약·선언·검사 | 완료 |
| 3 코어·셸 + 배포 골격 | 완료 (시나리오 S) |
| 4 스토리 모듈 | **완료** — `next-ai-poc` 에서 관리자·사용자 실측 통과 (`ci-947ea60b`) |
| 5 콘티·영상 모듈 + 시나리오 A·B | 대기 |
| 6 개발계 전환 | 이매지너스는 운영 우선 과제로 전환되어 **플랫폼 개통 멈춤**(선언 host → `next-imaginus`). 키이스트·legacy·와이랩·와이낫 대기 |
| 7 운영계 전환·정리 | 대기 |

진행 중 순서(순서 A, 이매지너스 제외 후): 키이스트 개발계 이관 → legacy 모듈(L-2~L-5) → 와이랩 → 5단계 → 와이낫 → 7단계.

주요 사실:

- **고객별 필요 모듈** (`platform/docs/customer-module-matrix.md`): 구현된 모듈은 story 하나. legacy·storyboard·video·video-scene 은 `module.yaml` 만 있다. 와이랩은 story 를 안 쓴다(`/api/story/` 호출 0, 전부 storyboard·video).
- **legacy 라벨 실데이터**(document·story_bible·story_output·script_job·character_sheet 합계): ai-poc 4 · 와이낫 4 · 키이스트 0 · 이매지너스(허브 dev 그래프) 0. `character_sheet` 는 원본 생성 코드가 저장소에 없다 → legacy 읽기 화면에서 제외, 라벨 소유(삭제 캐스케이드)만 유지.
- **와이랩 인풋 A~D** = 기존 `project.inputType`. 판정은 legacy 쪽 `documents.py` `KIND_SPECS`/`allowed_kinds()`. `legacyInputType` 은 화면 표시 플래그일 뿐.
- 셸·core-api 는 같은 태그로 배포, **항상 함께 빌드**(`.shell-unit-changes` 앵커). 모듈은 별도 이미지 `platform-mod-<id>`, 배포는 manual 잡.
- **알려진 결함 가능성**: `platform/core/**` 변경 시 셸·core-api 는 자동 배포되지만 모듈은 수동이라 옛 core 에 남는다. 이 버전 어긋남으로 `next-ai-poc` 에서 "저장하고 확정" 이 5xx 난 적이 있다(셸 `ci-0ca496ed` / 모듈 `ci-607988e0`). 재발 방지(모듈 동반 배포 또는 차단, `/api/health` 에 모듈 버전 보고) 확인 필요.
- 번들 캐시: 버전 경로만 `immutable`, 버전 없는 경로와 `STALE_BUNDLE` 은 `no-store`.

결정 레지스터 (멀티테넌트 dev):

| ID | 결정 |
|---|---|
| D-T01 | Neptune 은 고객별 전용 클러스터(합치지 않는다). 이유: `deduplicate_users` 가 기동마다 username 으로 병합, 관리자가 모두 `admin` |
| D-T02 | 개발계 ALB 하나 공유(IngressGroup + 호스트 규칙 + order 대역) |
| D-T03 | 호스트 `dev-<고객사>` |
| D-T04 | 기존 개발계는 두고 `next-` 로 검증 후 DNS 교체 |
| D-T05 | 네임스페이스는 테넌트 선언 `manageNamespace` → 그 테넌트 Application 에만 `CreateNamespace=true` (공용 ApplicationSet 동작 불변) |
| D-T06 | `manageServiceAccount` 구현 |

### 3.3 키이스트 운영계 구축 (별도 트랙)

- 목표: **개발계의 레거시 키이스트 앱을 그대로** 빈 운영 계정(722500516860)으로 옮긴다. 새 플랫폼 아님.
- 방식: VPC+EKS+노드그룹은 `eksctl` 설정 파일(저장소 커밋), Neptune·S3·IAM·ACM 은 재실행 가능한 CLI 스크립트(저장소 커밋). 운영 계정 ECR 신설 후 이미지 복사(허브 ECR 정책 변경 금지).
- `TOKEN_SECRET` 은 **새로 생성**(개발계와 같으면 개발 토큰으로 운영 진입 가능). 관리자 시드 새로. 데이터 복사 안 함.
- 운영 도메인 미정 → ALB 주소로 검증. `keyeast.meta-clouds.com`(개발계) 변경 금지.
- 산출: `platform/docs/keyeast-prod-manifest.md`, `cli-created.md`, `cost-log.md`.
- 고객 일정: 추석 전 프로토타입, 최종 2026-10-31. 고객 AWS 계정에 배포(데이터 소유권).
- **보안**: 사용자가 장기 액세스 키 원문을 채팅에 올린 적이 있다. 해당 키는 폐기·재발급 대상. 자격증명 값은 절대 출력·기록·커밋하지 않는다. 가능하면 배포용 IAM 역할을 만들어 assume 한다.

### 3.4 와이낫 장면 영상화 (`AI-POC-whynot/`)

- 지시서: `AI-POC-whynot/docs/prd.md` v1.4 · `prd2.md` v1.3 · `prd3.md` v1.1.
- 배포됨: Spec 01~06 (mock), 09 트랙 선택, 10 영상 프로젝트 폴더, 11 컷 순서·캐릭터 매칭, 단계 전진·진행률.
- 미구현: Spec 07 실제 영상(Seedance), 08 QA.
- 막힘: `docs/vendor/` 에 BytePlus ModelArk 원문 없음(공식 사이트가 SPA 라 자동 수집 불가, 사용자가 직접 저장해야 함). D-V04(크레딧 단위)·D-V06(규격)·D-V07(되돌리기 취소)·D-V16(컷 사이 전이) 전부 여기에 걸림.
- 정본 저장 구조 D-V15: S3 `users/{u}/video/{projectId}/project-state.json`(revision + CAS). Neptune 정점은 `project` 속성·`video_scene` 인덱스·`video_job`·`video_rating` 만.
- 목표 재정의: 웹툰은 컷마다 시간이 끊기지만 영상은 연속이어야 한다 — 컷 사이 빈 시간을 영상이 메운다(D-V16).
- 원본 웹툰 이미지의 BytePlus 전송은 서면 승인 전 금지(D-S06). `SEEDANCE_ALLOW_ORIGINAL_ASSETS=false`.

### 3.5 와이랩

- 개발계 신설 승인됨(G6b, 비용은 이매지너스와 같은 구성으로 본다).
- 새 기능 요청: 인풋 A(웹툰 원작)·B(소재·로그라인)·C(트리트먼트)·D(대본 1화)별로 AI 가 할 일을 다르게 하고 산출물을 여러 갈래로 제공. 입력 유형 판정은 기존 기능 재사용(새로 만들지 않음).
- **미결정 — 사용자 선택**: (1) 5단계까지 기다려 전체 이관 / (2) story 모듈을 와이랩에 추가로 켜서 각색·트리트먼트·대본·후속을 먼저 제공(콘티는 5단계). 판정 코드가 legacy 에 있어 (2) 도 legacy 모듈 선행.
- 조사 문서: `platform/docs/ylab-input-branch-research.md` (D-Y01~08). 확인된 공백: C 인풋에 허용 kind 없음, D 는 treatment 만 생성(주석과 구현 불일치).

---

## 4. 다음 기능 — 캐릭터 검색·추천 (이매지너스)

- 3단계 인물 생성에 붙인다. 카테고리·특성 키워드(예: 여자 주인공 + "톰보이") 입력 → 화면 오른쪽 패널에 비슷한 캐릭터가 나온 작품 추천.
- 국내 작품 먼저, 그다음 해외 유명작(기준: 국내 블로그·뉴스에 한 번이라도 언급된 작품).
- 방식: 웹 검색(이매지너스가 쓰는 Brave API) + LLM 정리.
- 조사 완료: `platform/docs/character-search-research.md` (D-C01~09).
- 선행 과제: `tools/web_search.py` 의 `country=KR`·`search_lang=ko` 하드코딩을 인자로(국내·해외 두 번 호출), 결과 0건 `ToolError` 를 빈 목록 경로로. 검색 캐시 없음.
- 저작권 경계: 결과는 참고로만 보여 주고 캐릭터 시트에 자동으로 채우지 않는다.
- 착수 조건: §0 이매지너스 운영 스토리 개발 확인 후. 이매지너스 운영 앱에 넣을지(운영 UI 유지) 플랫폼 story 모듈에 넣을지는 §0 결과를 보고 정한다.

---

## 5. 운영 원칙·승인 규칙

### 비용

POC 기준. **비용 상한을 미리 두지 않는다.** 실측하고 나중에 조정. 대신 모든 외부 호출(purpose·모델·토큰·시각)과 새로 만든 리소스(종류·이름·월 예상)를 `platform/docs/cost-log.md` 에 기록한다. 같은 요청이 반복 실패하며 재시도되는 루프는 비용이 아니라 결함 — 멈춘다.

### Terraform

**작업 계획에서 뺐다.** 새 인프라는 `eksctl` 설정 또는 재실행 가능한 CLI 스크립트로 만들고 저장소에 커밋한다. 기존 Terraform 코드·state 는 **건드리지 않는다** — 삭제 범위(계획에서만 제외 / 코드 삭제 / state 정리)는 사용자가 정한다. 조사 문서 `platform/docs/terraform-inventory.md`. `terraform apply`·`destroy` 금지.

### 승인 없이 해도 되는 것

- 허브 개발계 배포(push 파이프라인 + manual 잡)
- 읽기 전용 조회(모든 계정)
- 저장소 안 코드·문서·체커 변경, 커밋, 브랜치 push, MR 병합(CI green 확인 후)
- 새로 만드는 IRSA 역할·정책·SA·Secret (기존 것 수정은 불가). 병행 이관 시 `TOKEN_SECRET` 은 그 고객 레거시 값 복사, 신규·운영은 새로 생성
- 키이스트 운영 계정(빈 계정) 안 생성

### 승인이 필요한 것 (닿으면 그 항목만 건너뛰고 나머지는 계속)

- 운영 배포 (이매지너스 726990466389 쓰기 포함)
- 기존 IAM 역할·정책 수정, 허브 공용 정책(`GitLabRunner-ECR-Push` 등 — 버전 5개 상한)
- DNS 컷오버(기존 운영 호스트를 새 스택으로), 기존 레코드 변경(죽은 대상 수정은 예외적으로 승인된 적 있음)
- 데이터·리소스 삭제, 운영 데이터 복사
- 클러스터 범위 쓰기(ApplicationSet 적용 등)
- 원본 웹툰 이미지 외부 전송

### 금지

- 자격증명·시크릿 값 출력·기록·커밋
- `glab ci run`(수동 파이프라인) — `rules.changes` 가 전부 참이 되어 레거시 고객 배포가 켜진 사고가 있었다. 레거시 잡은 이제 `$CI_PIPELINE_SOURCE == "push"` 또는 `FORCE_DEPLOY_TENANT=<고객>` 일 때만 뜬다
- 쉘 문자열 치환으로 소스 수정(`f`→`r` 전역 치환 사고). 편집은 정확한 문자열 치환 도구로
- 체커 약화(범위 축소·단정 완화). 실패하면 코드를 고친다
- 공용 플랫폼 파일(`PLATFORM_FILES.txt`) 직접 수정 — 필요하면 어댑터·재수출로 우회
- 강제 push·reset·rebase

---

## 6. 작업 방식

- 조각 단위로 진행하고 조각마다 검증 → 커밋. **조각 중간에 멈추지 않는다.** 컨텍스트가 모자라면 새 조각을 시작하지 말고, 작업 트리를 깨끗이 하고 push·재개 지점·보고를 남긴 뒤 멈춘다.
- 재개 지점은 `platform/docs/unattended-log.md` 에 구체적으로(파일·줄·값). 다음 세션이 조사를 다시 하지 않도록.
- 검증의 정본은 CI. 브랜치 push → CI green → main 반영. push 직후 `git fetch origin && git log --oneline -1 origin/main` 으로 자기 커밋이 맨 위인지 확인(다른 세션이 main 을 자주 움직인다).
- 배포 확인은 파이프라인 success 가 아니라 **실측**: `/health`·`/api/health` 의 `sourceRevision`·`imageTag`, `/api/m/<module>/meta` 의 `version`. 셸·core-api·모듈 버전이 같아야 한다.
- 잡 상태가 `canceled` 여도 일이 일어났을 수 있다 — 트레이스를 끝까지 읽고 바깥 상태(ai-deploy 커밋, ArgoCD 리비전, 실제 이미지 태그)를 직접 확인.
- 비밀값이 필요한 실측은 배스천에서 실행하고 비밀이 아닌 결과(상태 코드·건수)만 돌려받는다. 로그인 흐름 실측은 사용자가 브라우저로 한다.
- 배스천 도구: `platform/tools/bastion_kubectl.ps1`(조회 전용), `bastion_graph_count.ps1`(Neptune 조회 전용, 쓰기 절 거부). 배스천 SG 는 Neptune SG `sg-05401ae26d7660ee5` 8182 에 추가돼 있고 이 SG 는 **네 고객 Neptune 이 공유**한다 — 쓰기 쿼리 금지.
- 지시가 틀렸으면 고치고 왜 다른지 적는다(과거 사례: `require_feature` 단일 인자, `ctx.api` 만으로는 blob·SSE 불가, `_renumber` 공용화).
- 모르는 것은 추측하지 말고 "확인 필요"로 남긴다.

### 보고 형식 (매번)

맨 위에 현황판 세 표 — 표 1 작업 단계(상태·완료 기준·막힌 것·남은 조각), 표 2 승인 대기, 표 3 다음 기능. 그 아래는 짧게: 조각별 커밋, 체커 수 변화, 새로 정한 판단(이번 것만), 고친 결함, 건너뛴 것, 재개 지점. 근거·분석 전문은 문서 파일에 두고 보고서엔 경로만.

---

## 7. 과거 사고와 교훈 (같은 실수 반복 금지)

| 사고 | 교훈 |
|---|---|
| Terraform 변경이 `AI-POC/**` 에 걸려 레거시 개발계 재배포 | CI `changes` 를 앱 경로로 좁혔다(Q-08). terraform·docs 변경이 앱 배포를 부르지 않는다 |
| `glab ci run` 이 레거시 배포 켬 | 수동 파이프라인 금지, 레거시 잡은 push 한정 |
| 모듈 파드 교착(비재진입 락 두 번) + 로그 0줄 | 진입점 import 스모크, `logging.basicConfig`, 정지는 스레드 + `join(timeout)` 으로 테스트 |
| 잡 러너 4종 미등록(라우트는 202, 잡은 영원히 queued) | `check_job_runners` 가 실제 import 로 선언·등록 대조 |
| 번들 URL 버전 계약 불이행, `after_request` 가 캐시 헤더 덮음 | 블루프린트 단독이 아니라 `create_app()` 전체 앱으로 검사 |
| 새 프로젝트가 "이전 방식" 으로 거부 | core-api 생성 → 모듈 진입 이음매 검사, 모듈 필드 없는 fixture |
| personalization 계산 미구현(주석만 있음) | 기능 → 능력 계산, `check_capability_features` |
| 셸·core-api 태그 스큐 | 함께 빌드, 폴백은 모든 저장소에 있는 태그 |
| ECR 불변 태그 충돌 | 태그 존재 시 빌드 skip(probe) |
| 줄 끝 공백으로 `git diff --check` 실패 | 저장 전 공백·BOM 제거 |
| "이매지너스는 레거시 없음" 오판 | 허브만 보고 운영 계정을 빠뜨림. **고객 판단 전에 운영 계정·운영 호스트부터 확인** |
| 명령문 자리표시자(`<…>`)가 채워지지 않은 채 전달 | 사용자 입력이 필요한 칸은 두지 말고 "대기"로 명시 |

---

## 8. 주요 문서 위치

| 문서 | 경로 |
|---|---|
| 모듈화 지시서 | `platform/docs/kiro-7steps.md` |
| 재개 지점·무인 진행 기록 | `platform/docs/unattended-log.md` |
| 이매지너스 운영 소스·대조 | `platform/docs/imaginus-prod-source.md` |
| 고객별 모듈 표 | `platform/docs/customer-module-matrix.md` |
| legacy 모듈 계획 | `platform/docs/legacy-module-plan.md` |
| 멀티테넌트 개발계 조사 | `platform/docs/multi-tenant-dev.md` |
| 캐릭터 검색 조사 | `platform/docs/character-search-research.md` |
| 와이랩 인풋 갈래 조사 | `platform/docs/ylab-input-branch-research.md` |
| 비용 기록 | `platform/docs/cost-log.md` |
| CLI 로 만든 리소스 | `platform/docs/cli-created.md` |
| Terraform 인벤토리 | `platform/docs/terraform-inventory.md` |
| next-ai-poc 사용 안내 | `platform/docs/next-ai-poc-user-guide.md` |
| 사고 기록 | `platform/docs/incident-*.md` |
| story 모듈 라우트 대조표 | `platform/modules/story/ROUTES.md` |
| 와이낫 PRD | `AI-POC-whynot/docs/prd.md`·`prd2.md`·`prd3.md` |
| 이매지너스 구조 분석(구) | `구조분석.md` (2026-09-08, 계정 726990466389 기준) |
