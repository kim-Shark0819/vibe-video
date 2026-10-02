# CLAUDE.md — AI POC 프로젝트 인수인계 (Kiro → Claude Code)

작성 2026-09-28. 이 파일은 작업 폴더 루트에 둔다. Claude Code 는 시작할 때 이 파일을 자동으로 읽는다.
지금까지 Kiro 로 진행한 작업의 상태·결정·규칙을 담았다. **이 파일과 저장소의 문서가 다르면 저장소 문서가 최신이다** — 특히 `platform/docs/unattended-log.md` 의 마지막 재개 지점을 먼저 확인할 것.

---

## 0. 지금 가장 먼저 할 일

> **2026-10-02 설계자 방침 — 아래 모든 항목보다 우선한다**
>
> - 통합계정(`730335451955`)에 AI POC 과금 0. AI POC 개발 환경·개발 도구(GitLab·Runner·ArgoCD·ECR·배스천)·모델 호출을 각 고객사 계정으로 옮긴다. 고객사 계정 비용은 늘어도 된다.
> - **통합계정 신규 생성 중지**(§5 금지 F-1). 0/0 인 앱도 다시 켜지 않는다. 이 문서의 허브 개발계 계획(§1 개발계 호스트, §3.2 진행 순서, §3.5 와이랩 개발계)은 이 방침에 맞춰 멈췄다.
> - **1단계 = dev 만 이관, 운영은 그대로**(운영 EKS·운영 앱·운영 배포 경로 무변경). 운영 연결과 통합계정 공용 자원 정리는 다음 단계(별도 지시). 어느 쪽인지 모르는 자원은 운영으로 본다.
> - Kiro 명령: `docs/kiro-command-dev-only.md` · 지시: `docs/kiro-instruction-2026-10-02.md` · 검토: `docs/dev-migration-review.md`

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
| **이매지너스 운영** | `726990466389` (story-ai) | `imaginus.meta-clouds.com`, ALB `story-ai-758721242`, **배스천 빌드 배포**(GitLab CI 아님, 설계자 `deploy.ps1`, 9-30 v89). 프로파일 `imaginus-prod`(10-02 Kiro 사용), 읽기 전용 `imaginus-prod-ro` 예정. **읽기 전면 허용 · 기존 `story-ai-*` 쓰기 금지**(§5 이매지너스 규칙) |
| 키이스트 운영 | `722500516860` | 9-30 부터 운영 중(`keyeast-prod-eks`, `keyeast.meta-clouds.com`). 프로파일 `keyeast-prod`, `keyeast-prod-deploy` |
| 와이낫 운영 | `089540175779` | `whynot.meta-clouds.com`, `whynot-prod-eks`. 프로파일 `whynot-prod`(10-02 Kiro 사용) |
| 와이랩 운영 | `892278727066` | `ylab-prod-eks`(배포는 CodeBuild). 프로파일 `ylab` |

**이 표가 계정 대장(정본)이다.** 계정 번호는 여기서만 복사하고 `python tools/check_accounts.py` 로 검사한다. 표를 바꾸면 그 체커의 `ACCOUNTS` 도 바꾼다.
(사고: `PRD_modular-platform.md` §4.2 에 이매지너스 계정을 와이랩 번호 `892278727066` 으로 적었다 — 10-02 정정 지시)

로컬 AWS 프로파일: `default · rosa-maker · mtp_ksb · ai-poc-hub · ylab · keyeast-prod · keyeast-prod-deploy · goodrich-mgmt` + 10-02 Kiro 사용 확인 `whynot-prod · imaginus-prod`.
**계정 혼용 금지.** 명령 전 `aws sts get-caller-identity --profile <p>` 로 계정을 확인하고 다르면 멈춘다.

### 개발계 호스트 (허브)

| 호스트 | 무엇 | 상태 |
|---|---|---|
| `ai-poc-web.meta-clouds.com` | AI-POC 레거시 앱 | `ci-def69090`, 무변경 유지 |
| `next-ai-poc.meta-clouds.com` | **새 모듈 플랫폼**(셸 + story 모듈)을 ai-poc 개발계 데이터 위에 올린 검증용 | 운영 UI 와 다르다. 운영의 새 버전이 아니다 |
| `dev-keyeast.meta-clouds.com` | 키이스트 개발계 (9-30 이전 이름 `keyeast.meta-clouds.com` 은 이제 **키이스트 운영**) | 스토리 개발 7단계 + personalization 원본. 10-02 0/0 |
| `dev-whynot.meta-clouds.com` | 와이낫 개발계 | 장면 영상화 · vpoc2. 10-02 0/0 · 503 |
| `dev-imaginus.meta-clouds.com` | DNS 는 `platform-dev-alb` 를 가리킴, 규칙 없음(404) | F-1 로 쓰지 않는다. 이매지너스 dev 는 이매지너스 계정에 만든다 |

**2026-10-02 F-1:** 이 표의 호스트는 모두 통합계정 자원이다. 새 호스트를 여기에 만들지 않고, 고객사 계정으로 옮기거나 지운다. 10-02 Kiro 실측: ns `ylab`(2/2, 동결) 외 전부 0/0.

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
**2026-10-02 중지(F-1).** 이 순서는 통합계정에 개발계를 세우는 일이라 멈춘다. 플랫폼 검증은 파일럿 고객사(와이낫) dev 에서 한다(Kiro 지시 D-A4).

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
| D-T02 | 개발계 ALB 하나 공유(IngressGroup + 호스트 규칙 + order 대역) — **2026-10-02 폐기(F-1).** 개발계는 고객사 계정마다 |
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

- 개발계 신설 승인됨(G6b, 비용은 이매지너스와 같은 구성으로 본다) → 통합계정에 생성됨(10-01, ns `ylab` · Neptune `ylab-graph`). **10-02 F-1 로 동결.** 와이랩 dev 는 와이랩 계정에 새로 만든다.
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

- 허브 개발계 배포: 이미 있는 앱의 코드 갱신만(push 파이프라인, 0/0 인 앱은 0/0 그대로). 새 테넌트·호스트를 여는 배포와 모듈 manual 배포 잡은 F-1 로 금지
- 읽기 전용 조회(모든 계정 — 이매지너스 포함. 계정 단위 조회 금지는 두지 않는다, R-1)
- 저장소 안 코드·문서·체커 변경, 커밋, 브랜치 push, MR 병합(CI green 확인 후)
- 새로 만드는 IRSA 역할·정책·SA·Secret — **고객사 계정 안에서만**(통합계정은 F-1). 기존 것 수정은 불가. 병행 이관 시 `TOKEN_SECRET` 은 그 고객 레거시 값 복사, 신규·운영은 새로 생성
- 고객사 계정 안 dev 자원 신규 생성(이관 작업, Kiro 지시 §3). 기존 운영 자원 수정은 승인 필요

### 승인이 필요한 것 (닿으면 그 항목만 건너뛰고 나머지는 계속)

- 운영 배포 (이매지너스 726990466389 쓰기 포함)
- 기존 IAM 역할·정책 수정, 허브 공용 정책(`GitLabRunner-ECR-Push` 등 — 버전 5개 상한)
- DNS 컷오버(기존 운영 호스트를 새 스택으로), 기존 레코드 변경(죽은 대상 수정은 예외적으로 승인된 적 있음)
- 데이터·리소스 삭제, 운영 데이터 복사
- 클러스터 범위 쓰기(ApplicationSet 적용 등)
- 원본 웹툰 이미지 외부 전송

### 금지

- **F-1 통합계정(`730335451955`) AI POC 신규 생성** (2026-10-02 설계자 지시). EKS·노드그룹·Neptune·ALB·리스너 규칙·Ingress 호스트·ECR 저장소·S3 버킷·IAM 역할/정책·네임스페이스·Route53 레코드·ACM 인증서·Secrets Manager·EC2 전부. 모듈형 플랫폼 작업 포함. 0/0 인 앱 재기동과 통합계정 모델 실호출(실호출 점검 스크립트 포함)도 금지. ns `ylab`·`ylab-graph` 는 동결(끄지도 지우지도 않음). 예외 E-1: `meta-clouds.com` 존에 `dev.<고객>.meta-clouds.com` NS 위임 레코드 고객당 1건(추가만, 설계자 10-02 승인). 해제 조건: 설계자 지시뿐
- 자격증명·시크릿 값 출력·기록·커밋
- `glab ci run`(수동 파이프라인) — `rules.changes` 가 전부 참이 되어 레거시 고객 배포가 켜진 사고가 있었다. 레거시 잡은 이제 `$CI_PIPELINE_SOURCE == "push"` 또는 `FORCE_DEPLOY_TENANT=<고객>` 일 때만 뜬다
- 쉘 문자열 치환으로 소스 수정(`f`→`r` 전역 치환 사고). 편집은 정확한 문자열 치환 도구로
- 체커 약화(범위 축소·단정 완화). 실패하면 코드를 고친다
- 공용 플랫폼 파일(`PLATFORM_FILES.txt`) 직접 수정 — 필요하면 어댑터·재수출로 우회
- 강제 push·reset·rebase

### 이매지너스 계정 (`726990466389`) — 2026-10-02 개정

예전 가드레일("STS 외 호출 금지, 프로필 만들지 않음")은 폐지했다. 원래 이유는 코드 병합 작업 때 그 계정 자격증명과 그 계정용 Terraform 이 한 폴더에 있어 잘못 apply 하는 것을 막는 것이었다. 그 작업이 끝난 뒤에도 남아 운영 확인을 막았고, "레거시 없음" 오판(§7)을 낳았다.

- IM-1 **읽기 전면 허용**(AWS 조회·공개 HTTP). 읽기는 읽기 전용 역할(`agent-readonly`, 프로필 `imaginus-prod-ro`)로 한다. S3 객체 내용·Secret 값·tfstate 는 읽지 않는다
- IM-2 기존 `story-ai-*`(EKS·ALB·Neptune·IAM·ECR·S3) 쓰기 금지. 예외: 새로 만드는 읽기 전용 역할 1건(설계자 10-02 승인). `story-ai-eks` 읽기 전용 access entry 는 운영 클러스터 변경이라 1단계에서 하지 않는다(지시 §10 N-6). `imaginus.meta-clouds.com` 레코드 변경 금지. 운영 배포는 설계자 `deploy.ps1`(워크스페이스 `이매지너스/`)
- IM-3 `이매지너스/terraform_infra/` 의 tfstate 를 열지 않고 그 폴더에서 terraform 명령을 실행하지 않는다
- IM-4 이 계정에 쓰는 명령 직전 `sts get-caller-identity` 결과와 대상 이름(`story-ai-*` 아님)을 확인한다. 다르면 멈춘다

### 규칙을 만들 때 — 가드레일 부작용 방지 (2026-10-02)

- R-1 계정 단위 "호출 금지"를 두지 않는다. 막을 것은 쓰기를 자원·동작 단위로 적는다. 운영 계정은 모두 읽기 허용
- R-2 금지 규칙에는 이유·범위·해제 조건을 함께 적는다. 이유가 된 작업이 끝나면 그 완료 보고에 "이 규칙 해제 여부"를 넣는다
- R-3 볼 수 없는 계정·호스트·저장소가 있으면 그 대상에 대해 "없다·같다·안 쓴다" 같은 결론을 내리지 않는다. "확인 필요 — 접근 불가(이유)"로 쓰고 접근을 요청한다
- R-4 고객에 대해 판단하기 전에 그 고객의 운영 계정·운영 호스트를 먼저 조회한다
- R-5 계정 번호는 §1 계정 대장에서만 복사한다. 새로 적은 번호는 sts 결과로 대조하고 `tools/check_accounts.py` 를 통과시킨다

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
| "이매지너스는 레거시 없음" 오판 | 허브만 보고 운영 계정을 빠뜨림. **고객 판단 전에 운영 계정·운영 호스트부터 확인.** 원인은 이유가 끝난 뒤에도 남은 이매지너스 계정 "호출 금지" 가드레일 → 폐지, R-1~R-4 (2026-10-02) |
| PRD 에 이매지너스 계정을 와이랩 번호(`892278727066`)로 기재 | 계정 번호는 §1 계정 대장에서만 복사, `tools/check_accounts.py` 가 고객 이름과 번호의 짝을 검사(R-5) |
| 개발 이관 지시를 "운영 무접촉"으로 읽어 통합계정에 GitLab·ArgoCD·ECR 을 남기는 설계가 나옴 | 지시에 목적(통합계정 과금 0)을 먼저 쓴다. "그대로 둔다"는 재생성 금지인지 설정 변경 금지인지 구분해 쓴다 |
| Kiro 가 `check:accounts` 실패 상태로 MR !224 병합 (10-02) | 병합은 모든 잡 success 일 때만, 병합 후 main 파이프라인 확인 (Kiro 명령 W-1) |
| 공용 배스천을 두 작업이 동시에 써 결과가 섞임 (10-02) | 작업별 임시 디렉터리·KUBECONFIG, 로컬로 되는 조회는 배스천 안 씀 (W-4) |
| 비밀값(ARK_API_KEY)을 대화로 요청 (10-02) | Secrets Manager 에 이름만 만들고 설계자가 콘솔에서 값 입력 (W-5) |
| 명령문 자리표시자(`<…>`)가 채워지지 않은 채 전달 | 사용자 입력이 필요한 칸은 두지 말고 "대기"로 명시 |

---

## 8. 주요 문서 위치

| 문서 | 경로 |
|---|---|
| **개발 이관 Kiro 명령 — 1단계 dev 만** | `docs/kiro-command-dev-only.md` (vibe-video) |
| 개발 이관 Kiro 지시 (2026-10-02 개정 2) | `docs/kiro-instruction-2026-10-02.md` (vibe-video) |
| 개발 이관 지시 해석 검토 | `docs/dev-migration-review.md` (vibe-video) |
| 계정 번호 검사 | `tools/check_accounts.py` (vibe-video) |
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
