# Kiro 지시 — 개발 환경 고객사 이관 (2026-10-02 개정 2)

| 항목 | 내용 |
|---|---|
| 받는 쪽 | Kiro (`awstech/ai`, 로컬 `C:\dev\ai`) |
| **이번 범위** | **1단계 = 개발(dev) 이관만. 운영은 하나도 바꾸지 않는다.** 운영 연결·통합계정 공용 자원 정리는 §10 "다음 단계"이며 이번에 하지 않는다 |
| 명령 | `docs/kiro-command-dev-only.md` 와 함께 받는다. 둘이 다르면 명령이 우선이다 |
| 대체하는 것 | 10-02 첫 지시의 조건 1~5, `현황정리.md` §6 결정 대기 목록, 이 문서의 개정 1 |
| 근거 | 설계자 지시(10-02) · 검토 문서 `docs/dev-migration-review.md`(참고용) |
| 결정 칸 | 설계자가 "대기 칸을 채워라"로 위임해 Claude Code 가 채웠다. 설계자가 바꾸면 그쪽이 우선이다 |

---

## 0. 오늘 바로 (다른 작업보다 먼저)

### 0-1 통합계정 신규 생성 중지 — 규칙 F-1 (설계자 지시, 2026-10-02)

통합계정(730335451955)에 AI POC 자원을 새로 만들지 않는다. 필요하면 고객사 계정에 만든다.

| 구분 | 내용 |
|---|---|
| 만들지 않는다 | EKS 클러스터·노드그룹 · Neptune · ALB·리스너 규칙·Ingress 호스트 · ECR 저장소 · S3 버킷 · IAM 역할·정책 · 네임스페이스 · Route53 레코드 · ACM 인증서 · Secrets Manager · EC2 |
| 예외 E-1 | `meta-clouds.com` 존에 `dev.<고객>.meta-clouds.com` 을 고객사 계정 존으로 넘기는 **NS 위임 레코드** 고객당 1건(비용 0, 추가만, 기존 레코드 무변경). 설계자 10-02 승인 |
| 다시 켜지 않는다 | 지금 0/0 인 앱(`ai-poc`·`platform-*`·`whynot`·`imaginus`·`keyeast`). 켜야 하면 설계자 승인 |
| 동결 | ns `ylab`(2/2) · Neptune `ylab-graph`(10-01 생성). 끄지도 지우지도 않고 그대로 둔다. 누가 왜 만들었는지 보고한다 |
| 모델 호출 | 통합계정에서 모델을 실제로 부르지 않는다(예: `keyeast_dev_flow_check.ps1` 같은 실호출 점검) |
| CI | 통합계정에 새 테넌트·호스트를 여는 배포 잡을 실행하지 않는다. 모듈 manual 배포 잡은 누르지 않는다 |
| 허용 | 조회 · 이미 있는 앱의 코드 갱신 배포(0/0 인 앱은 0/0 그대로) · **운영에 필요한 이미지 build·push 와 운영 승격 잡은 지금처럼 동작한다** |
| 삭제 | 설계자 승인 후에만 |

모듈형 플랫폼 작업(`PRD_modular-platform.md`)도 마찬가지다. 그 작업의 "키이스트 개발계 이관 → legacy → 와이랩 …" 순서는 멈춘다.
플랫폼 검증은 고객사 dev 에서 한다(§6 D-A4).

### 0-2 이매지너스 가드레일 개정 — 운영을 볼 수 있게, 부작용이 없게

`.kiro/steering/guardrails.md` 의 IM-1~3(R4)을 §8-1 블록(R5)으로 바꾼다. 요점은 이렇다.

- 이매지너스 계정 726990466389 은 **읽기 전면 허용**이다. 계정 단위 호출 금지는 두지 않는다.
- 읽기 자격을 새로 만든다(설계자 10-02 지시 "운영을 볼 수 있도록 고쳐라"로 승인). 새로 만드는 것이고 기존 운영 자원은 바꾸지 않는다.
  만들기 전에 되돌리는 방법을 `cli-created.md` 에 먼저 적는다.

| # | 만들 것 | 값 | 되돌리기 |
|---|---|---|---|
| V-1 | 읽기 전용 IAM 역할 | 이름 `agent-readonly`, 정책 AWS 관리형 `ReadOnlyAccess`, 신뢰 주체 = 지금 `imaginus-prod` 프로필의 IAM 주체. 로컬 프로필 `imaginus-prod-ro` 가 이 역할을 assume | 역할 삭제 |

- `story-ai-eks` 내부(kubectl) 조회용 access entry 는 운영 클러스터 설정 변경이라 **이번에 하지 않는다**(§10 N-6).
- 읽기 역할로도 S3 객체 내용·Secret 값·tfstate 는 읽지 않는다.
- `imaginus-prod` 의 키는 채팅에 노출된 키다. 설계자가 교체해도 V-1 신뢰 주체(IAM 사용자)는 그대로라 역할은 계속 쓸 수 있다.

### 0-3 계정번호 정정

`PRD_modular-platform.md` §4.2 의 이매지너스 계정 기재를 고친다(§8-2). `check_accounts.py` 를 저장소에 넣고 전체를 검사한다(§8-6).

### 0-4 실측 (읽기 전용)

| # | 무엇 | 왜 |
|---|---|---|
| M-1 | 통합계정 최근 30일 비용을 서비스별로 (Cost Explorer). 모델 호출(Bedrock·Marketplace) 포함 | 다음 단계 "0 으로 만들 목록"의 기준 |
| M-2 | 통합계정 dev 앱이 9-30 이후 0/0 이 된 경위 (ai-deploy 커밋·ArgoCD 이력) | 9-30 에는 dev-whynot·dev-keyeast 가 떠 있었다 |
| M-3 | 고객별 통합계정 dev 데이터 건수 (Neptune 정점 수 · S3 객체 수·용량) | 파드 0/0 은 데이터가 없다는 뜻이 아니다(D-D) |
| M-4 | `gitlab.meta-clouds.com` 서버 용도 — AI POC 외 그룹·프로젝트가 있는가, 어느 계정의 어떤 자원에서 도는가 | 다음 단계 N-3 |
| M-5 | Seedance Marketplace 계약(9-09~10-09, 갱신 옵트아웃)이 어느 계정에 있나 | 10-09 전에 |
| M-6 | 이매지너스 `deploy.ps1` 이 쓰는 배스천·빌드 자원이 어느 계정에 있나 (워크스페이스 `이매지너스/` 의 스크립트를 읽는다) | 그 자원은 운영이다. 지우지 않는다 |
| M-0 | **운영 기준값** — 고객 4곳 운영 `/api/health` 의 `imageTag`·`sourceRevision`, 운영 EKS `describe-cluster` 의 `publicAccessCidrs`, access entry 목록, 통합계정 ArgoCD 운영 앱 리비전 | 1단계가 끝났을 때 같아야 한다(운영 무변경 증거) |

---

## 1. 목적

최종 목적은 통합계정(730335451955)에서 AI POC 비용을 0 으로 만드는 것이다. 고객사 계정 비용은 많이 늘어도 된다.
비용을 줄이는 작업이 아니라, 비용이 나는 계정을 옮기는 작업이다.

**이번(1단계)은 그중 개발(dev)만 옮긴다.** 운영은 지금 경로(통합계정 GitLab·Runner·ArgoCD·ECR 등)로 계속 배포되므로,
1단계가 끝나도 통합계정에 운영 배포 경로가 남는다. **정상이다.** 그 정리는 다음 단계(§10)에서 별도 지시로 한다.

## 2. 용어 — 이 정의대로만 판단한다

| 용어 | 포함하는 것 |
|---|---|
| **운영** | 고객사 운영 EKS 4개(`whynot-prod-eks`·`keyeast-prod-eks`·`ylab-prod-eks`·`story-ai-eks`)와 그 안의 앱·설정, 운영 Neptune·S3·ALB·IAM, 운영 도메인 레코드·인증서, **운영을 배포하는 지금 경로 전부**: 통합계정 GitLab·Runner·ArgoCD·ECR·`ArgoCD-CrossAccount-Deployer`·`<고객>-argocd-deployer`·NAT `13.125.117.242`·배스천·`AI-POC-eks` 클러스터 자체, 와이랩 CodeBuild, 이매지너스 `deploy.ps1` 과 그 빌드 자원 |
| **개발(dev)** | 통합계정 `AI-POC-eks` 안의 고객 네임스페이스(`whynot`·`keyeast`·`imaginus`·`ylab`)와 그 앱, dev 전용 Neptune(`whynot-graph`·`keyeast-graph`·`imaginus-graph`·`ylab-graph`), dev 전용 ALB(`whynot-web-alb`·`keyeast-web-alb`), 노드그룹 `keyeast-ng`, dev S3(`<고객>-730335451955`, `whynot-video-730335451955-us-west-2`), dev 호스트(`dev-whynot`·`dev-keyeast`·`dev-imaginus`·`dev-ylab`), 모듈형 플랫폼 dev 자원(`platform-dev-alb`·`platform-*` ECR·ns `ai-poc` 의 `platform-*`·`next-ai-poc`). 운영 경로 안의 dev 몫 세 가지: 통합계정 ArgoCD 의 `<고객>-dev` 앱, 통합계정 CI 의 `deploy:<고객>:dev` 잡, ai-deploy 의 `<고객>/dev` 경로 (ArgoCD·CI·ai-deploy 자체와 운영 몫은 운영이다) |
| **경계 불명** | 둘 다에 걸리거나 어느 쪽인지 확인이 안 된 자원 → **운영으로 본다.** 바꾸지도 지우지도 않고 보고한다 |
| **옮긴다** | 고객사 계정에 dev 를 새로 만들고(빈 데이터), 같은 앱을 띄워 검증한 뒤, 통합계정의 그 고객 dev 자원을 지운다(승인 후) |

## 3. 고객사 계정마다 만들 것 (1단계)

1. dev VPC 1개 + dev EKS 1개 (CIDR 는 현황정리 §7 배정안). eksctl 설정 + CLI 스크립트(D-C)
2. GitLab + Runner + ArgoCD — 통합계정 구성을 복제한다. **ArgoCD 대상은 그 계정의 dev EKS 하나뿐이다.** 운영 EKS 를 등록하지 않는다
3. ECR · dev Neptune · dev S3 · IRSA · ALB · ACM
4. Route53 서브존 `dev.<고객>.meta-clouds.com` (부모 존 NS 위임 = F-1 예외 E-1). dev 앱·GitLab·ArgoCD 주소는 모두 이 서브존 아래
5. 모델 호출(Bedrock)도 이 계정에서. 모델 접근 활성화는 해도 된다. **Marketplace 구독·계약이 필요하면 설계자에게 요청하고 기다린다**
6. 새로 만든 자원은 `platform/docs/cli-created.md` · `cost-log.md` 에 적는다. GitLab 초기 관리자 비밀번호 등 비밀은 그 계정 Secrets Manager 에만 두고 출력하지 않는다

배포 경로(1단계): 코드 정본 → 고객사 GitLab CI → 고객사 ECR → 고객사 ArgoCD → 고객사 dev EKS.

## 4. 운영 — 1단계에서 하지 않는 것

아래는 **하나도 하지 않는다.** 필요해 보이면 멈추고 보고한다.

- 운영 EKS 설정 변경 (허용 IP · access entry · 노드그룹 · 애드온 · 인증 모드)
- 운영 앱 · 매니페스트 · 이미지 태그 · 레플리카 변경, 운영 배포 실행
- 새 ArgoCD 에 운영 EKS 등록
- 운영 이미지 위치 변경 (운영은 계속 통합계정 ECR 에서 pull 한다)
- 운영 도메인 레코드 · 인증서 변경
- 운영 배포 경로(§2 "운영"의 경로 전부) 변경 · 삭제
- 통합계정 CI 의 build · probe · `deploy:<고객>:prod` 잡 변경. **운영 승격이 통합계정 ECR 이미지에 의존한다**
- `story-ai-*` 쓰기, 운영 데이터 복사

## 5. 순서

고객사 하나씩: **와이낫(파일럿) → 키이스트 → 와이랩 → 이매지너스.** 다음 고객은 앞 고객 승인 후 시작한다.

각 고객사마다:

1. 고객사 계정에 §3 을 만든다
2. 코드를 고객사 GitLab 에 넣고(D-E) dev 앱을 배포·검증한다
3. 완료 기준(§9)을 보고하고 설계자 검토를 받는다
4. 승인 후 통합계정의 그 고객 dev 자원을 지운다: §2 "개발"의 그 고객 몫 + 통합계정 CI 의 `deploy:<고객>:dev` 잡 끄기 + 통합계정 ArgoCD 의 `<고객>-dev` 앱 삭제 + `dev-<고객>` 레코드 삭제.
   지우기 전에 각 자원이 운영에서 참조되지 않는다는 근거를 보인다
5. 모듈형 플랫폼 dev 자원(§2)은 플랫폼 검증을 와이낫 dev 로 옮긴 뒤 같은 방식으로 지운다(승인 후)

## 6. 결정 사항 (10-02, 설계자 위임으로 채움)

| ID | 질문 | 결정 |
|---|---|---|
| D-A2 | dev 도메인 | 고객사 계정에 서브존 `dev.<고객>.meta-clouds.com` 을 만들고 부모 존에 NS 위임 1건(E-1). 기존 레코드는 바꾸지 않는다. 옛 `dev-<고객>` 레코드는 그 고객 dev 정리 때 지운다(승인 후) |
| D-A3 | AI-POC 기준 앱 | 다시 켜지 않는다(현황정리 D-11 = 아니오). `AI-POC-eks` 위에서 운영용 ArgoCD 가 돌기 때문에 1단계에서는 지우지 않는다(§10) |
| D-A4 | 모듈형 플랫폼 | 통합계정에서는 멈춘다(F-1). 검증은 와이낫 dev 에서 `next.dev.whynot.meta-clouds.com` 같은 서브존 아래 호스트로 한다. 통합계정 플랫폼 dev 자원은 §5-5 로 지운다 |
| D-C | 새 인프라 도구 | **eksctl 설정 + 재실행 가능한 CLI 스크립트**, 저장소에 커밋한다(9-28 규칙 유지). Terraform 은 쓰지 않는다. 와이랩 `AI-POC-ylab/terraform/prod/10-ylab` 와 키이스트 운영계 산출물(`platform/docs/keyeast-prod-manifest.md`·`cli-created.md`)은 참고만 한다 |
| D-D | 통합계정 dev 데이터(Neptune·S3) | **옮기지 않는다.** 새 dev 는 빈 상태로 시작한다. 삭제 전에 M-3 건수를 보고하고, 설계자가 지정한 것만 그 고객 계정으로 복사한다 |
| D-E | 1단계 코드 정본과 고객사 GitLab | 정본은 지금 그대로다 — 와이낫·키이스트·와이랩은 `awstech/ai`, 이매지너스는 워크스페이스 `이매지너스/`. 고객사 GitLab 은 **그 고객 디렉터리 + 공통 플랫폼 파일만** 단방향으로 받는다. 전체 저장소 미러 금지(다른 고객 코드가 들어간다). `awstech/ai` 쪽 CI 잡이 골라서 push 한다. 고객사 GitLab 에서 직접 커밋하지 않는다. 공통 파일 드리프트 검사는 지금처럼 `awstech/ai` 에서 돈다 |
| D-F | 파일럿 고객사 | 와이낫 (현황정리 D-06 동의) |
| D-G | 와이낫 vpoc2 설계자 테스트 | 와이낫 계정 dev(`dev.whynot.meta-clouds.com`)에서 한다. 통합계정 dev-whynot 은 다시 켜지 않는다(F-1) |
| D-H | 현황정리 D-10 (모듈형 플랫폼과의 관계) | (c) 를 고쳐서 채택한다. 두 작업을 다 살리되 플랫폼 검증도 고객사 계정에서 한다(D-A4) |

## 7. 고객별 주의

- 와이낫·키이스트: 운영이 통합계정 ArgoCD·ECR 에 의존한다. 그 경로는 1단계에서 건드리지 않는다.
- 와이랩: 운영 배포는 CodeBuild 그대로다. 통합계정 ns `ylab`·`ylab-graph` 는 동결(F-1)이고, 와이랩 dev 는 와이랩 계정에 새로 만든다.
  동결 자원의 삭제는 와이랩 dev 정리(§5-4) 때 함께 승인받는다.
- 이매지너스:
  - 운영(`story-ai-*`)은 설계자가 워크스페이스 `이매지너스/` 소스로 `deploy.ps1` 배포를 하고 있다(9-29~30 v87~v89). 그대로 둔다.
  - dev 는 그 소스로 만든다. `AI-POC-이매지너스/` 는 운영보다 뒤처져 있어 쓰지 않는다.
  - 그 저장소는 remote 가 없다(`a585a39` + 이후). 이매지너스 고객사 GitLab 으로 push 하면 그것이 첫 remote 가 된다.
    **push 전에 작업 트리에 커밋되지 않은 변경이 있으면 멈추고 보고한다**(커밋 여부는 설계자가 정한다).
  - dev 설정은 운영과 같은 키를 쓰고 값만 dev 용으로 한다(운영 빌드 아카이브의 렌더된 매니페스트 참고).
- 계정 번호는 §8-1 계정 대장에서만 복사한다.

---

## 8. 저장소 문서 수정 (Kiro 가 `awstech/ai` 에서. 커밋 → MR → CI green → 병합)

### 8-1 `.kiro/steering/guardrails.md` — 개정 R5

R4 의 IM-1~3 자리에 아래 블록을 넣는다. R4 원문은 "R4 (2026-10-02 대체)" 표시와 함께 이력으로 남긴다.

```
## 계정 대장 (정본 — 계정 번호는 여기서만 복사한다)
| 계정 | 번호 | 프로필 |
|---|---|---|
| 통합(허브) | 730335451955 | ai-poc-hub |
| 와이낫 운영 | 089540175779 | whynot-prod |
| 키이스트 운영 | 722500516860 | keyeast-prod · keyeast-prod-deploy |
| 와이랩 운영 | 892278727066 | ylab |
| 이매지너스 운영 | 726990466389 | imaginus-prod-ro (읽기) · imaginus-prod |

## F-1 통합계정 신규 생성 중지 (2026-10-02 설계자)
통합계정에 AI POC 자원을 새로 만들지 않는다. 0/0 인 앱을 다시 켜지 않는다.
예외 E-1: dev.<고객>.meta-clouds.com NS 위임 레코드 고객당 1건.
ns ylab · ylab-graph 는 동결. 통합계정에서 모델 실호출 금지. 삭제는 승인 후.

## 1단계 범위 (2026-10-02 설계자)
dev 만 옮긴다. 운영(고객사 운영 EKS 와 그 앱 · 운영 배포 경로 전부)은 바꾸지 않는다.
어느 쪽인지 모르는 자원은 운영으로 본다.

## 이매지너스 계정 — 개정 R5 (2026-10-02)
IM-1 읽기 전면 허용(AWS 조회 · 공개 HTTP). 계정 단위 호출 금지는 없다. 읽기는 imaginus-prod-ro 로 한다.
     S3 객체 내용 · Secret 값 · tfstate 는 읽지 않는다.
IM-2 기존 story-ai-* (EKS · ALB · Neptune · IAM · ECR · S3) 쓰기 금지.
     새로 만드는 읽기 전용 역할 agent-readonly 1건은 허용(설계자 10-02 승인). story-ai-eks access entry 는 1단계에서 하지 않는다.
     imaginus.meta-clouds.com 레코드 변경 금지.
     운영 배포는 설계자의 deploy.ps1(워크스페이스 이매지너스/)이 한다. 그 경로를 바꾸지 않는다.
IM-3 이매지너스/terraform_infra/ 의 tfstate(.backup)를 열지 않고(평문 비밀), 그 폴더에서 terraform 명령을 실행하지 않는다.
IM-4 이 계정에 쓰는 명령 직전 sts get-caller-identity 결과와 대상 이름(story-ai-* 가 아닌지)을 확인한다. 다르면 멈춘다.
신규 dev 자원 생성은 허용한다(1단계 범위).

## 규칙을 만들 때 — 가드레일 부작용 방지 (2026-10-02)
R-1 계정 단위 "호출 금지"를 두지 않는다. 막을 것은 쓰기를 자원·동작 단위로 적는다. 운영 계정은 모두 읽기 허용.
R-2 금지 규칙에는 이유 · 범위 · 해제 조건을 함께 적는다. 이유가 된 작업이 끝나면 그 완료 보고에 "이 규칙 해제 여부"를 넣는다.
R-3 볼 수 없는 계정 · 호스트 · 저장소가 있으면 그 대상에 대해 "없다 · 같다 · 안 쓴다" 같은 결론을 내리지 않는다.
    "확인 필요 — 접근 불가(이유)"로 쓰고 접근을 요청한다.
R-4 고객에 대해 판단하기 전에 그 고객의 운영 계정 · 운영 호스트를 먼저 조회한다.
R-5 계정 번호는 계정 대장에서만 복사한다. 새로 적은 번호는 sts 결과로 대조하고 check_accounts.py 를 통과시킨다.
```

### 8-2 `PRD_modular-platform.md`

| 위치 | 고칠 것 |
|---|---|
| §4.2 계정 기재 | 이매지너스 계정으로 적힌 와이랩 번호 892278727066 을 이매지너스 번호 726990466389 로 고친다. 옆에 "(2026-10-02 정정 — 이전 값은 와이랩 운영 계정 번호. sts get-access-key-info 로 확인)"을 붙인다 |
| §4.2 "가드레일은 D-M02 전까지 유지한다: 이 계정에는 STS 외 호출 금지." | 원문은 두고 바로 뒤에 "(2026-10-02 폐지 — guardrails.md R5 IM-1~4 로 대체)"를 붙인다 |
| D-M02 (해제 사다리) | "2026-10-02 해제 — 읽기 전면 허용(R5)" |
| D-M04 "와이랩 개발계 신설 — 보류(비용)" | "G6b 승인 → 통합계정에 생성(10-01) → 2026-10-02 F-1 로 동결. 와이랩 dev 는 와이랩 계정에 새로 만든다" |

### 8-3 `AI-POC/docs/PRD_AI-POC_DEV-EKS_Terraform.md` · `tasks.md`

§2.2 "이매지너스 계정의 리소스 접근·변경 (자격증명이 폴더에 있어도 사용 금지)", H4, H7, `tasks.md` 0.2.2 각각 뒤에
"(2026-10-02 폐지 — 코드 병합 작업 범위의 규칙이었다. 현재 규칙: guardrails.md R5)"를 붙인다. 원문은 지우지 않는다.

### 8-4 `docs/인프라-구조-현황.md`

키이스트 운영계가 "없다"는 서술을 고친다: 계정 722500516860 에 `keyeast-prod-eks` 운영 중, `keyeast.meta-clouds.com` = 키이스트 운영(9-30부터),
키이스트 개발 = `dev-keyeast.meta-clouds.com`(통합계정, 10-02 0/0).

### 8-5 결정 레지스터

`PRD_modular-platform.md` 또는 결정 레지스터에 이 문서 §6 의 결정을 옮겨 적는다. 멀티테넌트 dev 결정 D-T02(개발계 ALB 하나 공유)는 "2026-10-02 폐기(F-1)"로 표시한다.

### 8-6 계정 검사 체커

vibe-video 저장소 `tools/check_accounts.py` 를 `platform/tools/check_accounts.py` 로 복사한다.
`ROOT` 는 저장소 루트를 가리키게 고친다(`dirname` 세 번).
저장소 전체에 실행해 나오는 것을 고친다. 일부러 다른 고객 번호를 적는 줄에만 `account-check: ignore` 를 붙인다.
CI 검사 단계에 넣는다(배포 잡과 무관하게). 체커 기준을 완화하지 않는다.

---

## 9. 완료 기준 (고객사마다, §5-3 보고에 넣는다)

| # | 기준 |
|---|---|
| C-1 | `https://dev.<고객>.meta-clouds.com/api/health` 200, `imageTag` = 고객사 GitLab CI 태그, `sourceRevision` = 정본 커밋 |
| C-2 | 설계자가 브라우저로 로그인·주요 흐름 확인 (와이낫은 vpoc2 ①~⑤ 포함) |
| C-3 | **운영 무변경:** M-0 기준값(운영 `imageTag`·`sourceRevision`, `publicAccessCidrs`, access entry, 통합계정 ArgoCD 운영 앱 리비전)이 작업 전과 같다 |
| C-4 | **F-1 준수:** 통합계정에 새로 생긴 자원이 E-1 NS 레코드 말고는 0 이다 |
| C-5 | 고객사 GitLab 에 다른 고객 디렉터리가 없다 |
| C-6 | 지울 통합계정 dev 자원 목록과 자원마다 "운영이 참조하지 않는다"는 근거 |

## 10. 다음 단계 — 이번에 하지 않는다 (별도 지시로 시작)

1단계가 4곳 모두 끝나고 설계자가 별도로 지시하면 시작한다. 그 전에는 아래 어느 것도 하지 않는다.

| # | 내용 |
|---|---|
| N-1 | 새 ArgoCD 를 운영 EKS 에 연결 — 운영 EKS 허용 IP 추가 · access entry 추가 · 운영 이미지를 고객사 ECR 로 전환(같은 digest). 첫 동기화는 자동 동기화를 끄고 diff 확인 후 수동. 하나씩 승인 |
| N-2 | 와이랩(CodeBuild)·이매지너스(`deploy.ps1`) 운영도 GitLab → ArgoCD 로 전환. 이매지너스는 마지막 + 별도 승인 |
| N-3 | GitLab 서버 처리 — M-4 결과 AI POC 전용이면 삭제, 회사 공용이면 AI POC 프로젝트의 Runner·CI 변수·배포 키만 정리 |
| N-4 | 고객사 GitLab 을 그 고객 코드의 정본으로 전환. 공통 파일은 상류 한 곳 + 고객사 저장소 `platform.lock`(상류 태그·파일 해시), 드리프트 검사는 고객사 CI 에서 lock 해시 대조 |
| N-5 | 통합계정 공용 자원 삭제 — ArgoCD · Runner · `AI-POC-eks` · AI-POC 기준 앱(`ai-poc-graph` 포함, 데이터는 내보내지 않는다 — 비밀번호 해시) · AI-POC VPC(NAT 포함) · 배스천 · ECR · 통합계정 ACM. 운영 쪽 옛 연결(허용 IP `13.125.117.242`, `ArgoCD-CrossAccount-Deployer` 신뢰) 제거. 이것으로 통합계정 과금 0 |
| N-6 | `story-ai-eks` 읽기 전용 access entry (kubectl 조회용). 인증 모드가 `CONFIG_MAP` 이면 `aws-auth` 수정이 필요하므로 별도 판단 |
