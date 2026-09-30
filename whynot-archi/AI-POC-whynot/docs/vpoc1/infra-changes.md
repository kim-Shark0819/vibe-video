# vpoc1 인프라 변경 기록

D-L02 범위 안에서만 바꿨다. Terraform 은 실행하지 않았다.
모든 명령은 워크스테이션에서 `--profile ai-poc-hub`(계정 `730335451955`)로 돌렸다.

---

## 1. 영상 출력 버킷 — 변경 없음

D-L02(a)는 "us-west-2 영상 출력 버킷이 **없을 때만**" 새로 만들도록 허용한다.
Gate 0 C6 에서 이미 있는 것을 확인했으므로 **만들지 않았다**(E1 미발동).

| 시각 (UTC) | 명령 | 목적 | 결과 |
|---|---|---|---|
| 2026-09-23 06:12 | `aws s3api get-bucket-location --bucket whynot-video-730335451955-us-west-2` | 리전 확인 | `LocationConstraint: us-west-2` — 요구 리전과 일치 |
| 2026-09-23 06:40 | `aws s3api get-bucket-encryption --bucket whynot-video-730335451955-us-west-2` | 기본 암호화 확인 | `AES256`(SSE-S3), `BucketKeyEnabled: true` |
| 2026-09-23 06:41 | `aws s3api get-bucket-policy --bucket whynot-video-730335451955-us-west-2` | 정책 확인 | `DenyInsecureTransport` 한 문장만. 퍼블릭 허용 문장 없음 |

버킷에 `ExpireRawProviderOutput` 라이프사이클 규칙이 걸려 있다(사전 점검 출력의
`Expiration: expiry-date="Wed, 07 Oct 2026 ..."` 로 확인). 원본 provider 출력은 2주 뒤 만료된다 —
`final.json` 에 출력 키를 기록해 두지만 **영상 파일 자체는 영구 보관이 아니다.** 2단계 인계 항목이다.

## 2. 앱 IRSA 인라인 정책 `vpoc1-luma` — 추가

D-L02(b)에 따라 **빠진 문장만** 넣었다. Gate 0 C5(IAM simulate) 결과 이미 허용된 것은
정책 파일에서 뺐다 — `bedrock:InvokeModel`(Luma·SD3.5·Claude), `bedrock:GetAsyncInvoke`,
`bedrock:ListAsyncInvokes`, 두 버킷의 `s3:PutObject`·`s3:GetObject` 는 모두 이미 allowed 였다.

빠져 있던 것은 **영상 버킷의 `s3:ListBucket` 하나**였다. 이것이 없으면 Luma 완료 후
출력 접두사를 나열해 `.mp4` 를 찾을 수 없다(PRD 5.1 — 파일명을 가정하지 않는다).

| 시각 (UTC) | 명령 | 목적 | 결과 |
|---|---|---|---|
| 2026-09-23 06:20 | `python AI-POC-whynot/tools/vpoc_preflight.py --profile ai-poc-hub --only C5` | 권한 격차 확인 | 10개 중 9개 allowed, `s3:ListBucket` on 영상 버킷 = `implicitDeny` |
| 2026-09-23 06:26 | `aws iam put-role-policy --role-name whynot-app-role --policy-name vpoc1-luma --policy-document file://AI-POC-whynot/docs/vpoc1/iam-vpoc1-luma.json` | 빠진 문장 추가 | 성공 |
| 2026-09-23 06:27 | `aws iam get-role-policy --role-name whynot-app-role --policy-name vpoc1-luma` | 적용 확인 | 문서 일치 |
| 2026-09-23 06:31 | `... --only C5` 재실행 | 재검사 | 10개 전부 `allowed` |

정책 문서는 `docs/vpoc1/iam-vpoc1-luma.json` 에 있다. 대상 역할 이름과 버킷 이름을 파일에
그대로 적었다 — 계정 ID 는 버킷 이름의 일부이고 이미 저장소의 `config.env.example` 에 있다.

> simulate 주의: `s3:ListBucket` 허용 문장에 `s3:prefix` 조건이 붙어 있어서 컨텍스트 키를
> 주지 않으면 `implicitDeny` 로 답한다. `vpoc_preflight.py` 는 `ContextEntries` 로
> `s3:prefix=users/` 를 넘긴다. 이것을 모르면 실제 권한이 있는데도 실패로 읽는다.

## 3. 바꾸지 않은 것

- 버킷 생성·삭제·정책 변경 없음
- Terraform 실행 없음 (`plan` 포함)
- `kubectl apply`/`edit`/`set`/`scale` 없음 — ArgoCD 가 관리한다. 조회도 EKS 엔드포인트가 사설이라 워크스테이션에서 불가했다
- Neptune·S3 데이터 삭제 없음
- 다른 고객 계정·리소스 접근 없음

## 4. Terraform 편입 대상

prod 배포 뒤 기존 원칙대로 Terraform 으로 옮긴다.

| 항목 | 현재 상태 | 편입 위치 후보 |
|---|---|---|
| IAM 인라인 정책 `vpoc1-luma`(영상 버킷 `s3:ListBucket`) | CLI 로 붙였다 | `terraform/hub/25-app-iam` — 앱 역할 정책에 문장 추가 |
| 영상 버킷의 `users/` 접두사 라이프사이클 | 기존 `ExpireRawProviderOutput` 규칙이 vpoc 출력에도 적용된다 | 완성본 보관이 필요하면 별도 접두사와 규칙을 Terraform 으로 정의 |
| Luma Ray2 동시 요청 쿼터(현재 1) | 기본값 | 상향이 필요하면 Service Quotas 인상 요청 — Terraform 대상 아님 |
| 운영 영상 버킷 | 없다 (`config.prod.env` 의 `VPOC_VIDEO_BUCKET=` 이 빈 값) | 운영 전환 시 `terraform/hub` 에 us-west-2 버킷 추가 |
