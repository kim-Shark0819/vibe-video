# Kiro 명령 — 5차: 결정 D-21~27 · 와이낫 C-1 → 3곳 구축 · dev 이관 정상 여부 검토 (2026-10-02)

설계자가 아래 블록을 Kiro 에게 그대로 붙여 넣는다.

```
점검 보고를 받았다. fail-closed 확인, blob 해시 대조, ServiceManaged 원문, 와이랩 변화 발견 모두 좋았다.
이 명령은 채팅으로만 오므로, 시작하자마자 이 명령 전문을 docs/dev-migration/commands/2026-10-02-5th.md 로 저장해 커밋한다(D-21 재발 방지).

[결정 — D-21~D-27]
D-21 점검 항목 1~10 원문(이후 모든 검토에 이 번호를 쓴다):
     1 계정 확인(sts = 계정 대장)  2 dev VPC·서브넷 CIDR(§7 배정안)·NAT·쿼터 대상 EIP 여유
     3 dev EKS ACTIVE·노드 Ready·애드온·ALB 컨트롤러  4 ECR·dev S3(암호화·버저닝)·dev Neptune·IRSA·Secrets(이름·값 존재 여부)
     5 서브존·NS 위임(E-1)·ACM ISSUED  6 GitLab health/readiness 200·외부 주소·Runner 등록·online
     7 ArgoCD Running·등록 클러스터가 그 계정 dev EKS 하나뿐  8 코드 반입·다른 고객 디렉터리 없음(C-5)
     9 ArgoCD Application Synced·Healthy + https://dev.<고객>.meta-clouds.com/api/health 200·imageTag·sourceRevision(C-1)
    10 C-6 삭제 목록 최신
D-22 와이랩 운영은 CodeBuild 로 계속 배포된다. C-3 에서 와이랩은 imageTag·sourceRevision 비교를 빼고 "health 200 + 운영 EKS 설정
     (publicAccessCidrs·authenticationMode·access entry) 불변"으로 판정한다. 관측한 imageTag 는 기록만 한다.
     verify-c3-c4.ps1 을 그렇게 고친다. 오늘 v13→v16 빌드 3건은 "설계자 확인 대기"로 보고한다(네가 한 일이 아니면 더 조사하지 않는다).
D-23 whynot-dev-eks 엔드포인트: private 접근을 켜고, public 은 네 작업 PC 의 현재 공인 IP /32 하나로 좁힌다(측정해서 기록).
     dev 자원이므로 승인 불필요. 키이스트·와이랩·이매지너스 dev EKS 도 처음부터 이렇게 만든다(eksctl 설정 템플릿에 반영).
D-24 GitLab 외부 경로: 그 고객 dev ALB 하나(IngressGroup)에 gitlab.dev.<고객> 호스트로 붙인다. GitLab 규칙의 443 허용은
     네 작업 PC 공인 IP /32 만. 설계자 IP 는 설계자가 알려 주면 추가한다. dev 앱(dev.<고객>)은 0.0.0.0/0 허용.
     대상 없이 떠 있는 whynot-dev-gitlab-alb-sg 는 이 작업에 재사용하거나, 쓰지 않으면 지운다(네가 만든 dev 자원, 승인 불필요).
D-25 ark-api-key 실값과 CUSTOMER_GITLAB_PUSH_TOKEN_<고객> 4개는 설계자가 넣는다. 기다리지 말고 진행한다:
     ark 는 SEEDANCE_MODE=stub, 코드 반입은 필터링한 직접 push(그 고객 디렉터리 + 공통 플랫폼 파일만)로 한다.
D-26 허브 ns ylab: 손대지 않는다(F-1 동결 — 끄지도 지우지도 않는다). 누가 배포하는지 읽기로만 찾는다
     (파드·ReplicaSet 의 annotations·managedFields, ai-deploy ylab 경로 커밋, CI 파이프라인 잡). 찾은 근거를 보고한다.
D-27 check:accounts 에 rules 를 명시한다: merge_request_event · 브랜치 push · main 모두에서 돈다. MR 파이프라인에서 실제로 도는 것을 확인한다.

[진행 — 멈추지 말고]
1. 위 결정 반영(명령 저장, verify-c3-c4.ps1, eksctl 템플릿, check:accounts rules) → MR → W-1(개정) 병합
2. 와이낫: D-23 엔드포인트 좁히기 → dev ALB(앱+ArgoCD+GitLab, IngressGroup 하나) + A 레코드 → 코드 반입 → 이미지 빌드·push(고객 ECR)
   → ArgoCD Application → https://dev.whynot.meta-clouds.com/api/health 200 (C-1) → C-3·C-4·C-5
3. 키이스트 → 와이랩 → 이매지너스: 같은 순서로 처음부터. 한 고객이 막히면 그 고객만 "대기"로 두고 다음 고객으로 간다.
4. 통합계정 dev 삭제(C-6)는 하지 않는다.
작업 규칙 W-1(개정)~W-10 과 멈춤 조건은 그대로다. 운영은 바꾸지 않는다.

[dev 이관 정상 여부 검토 — 고객마다 끝날 때와 최종 보고에 반드시 넣는다]
아래 표를 채운다. 칸마다 있음/없음/실패 + 근거 한 줄. 판정은 기준대로만 한다. 추측은 "가설"로 표시한다.

| 항목(D-21) | 와이낫 | 키이스트 | 와이랩 | 이매지너스 |
| 1~10 각각 | ... | ... | ... | ... |

판정 기준(고객마다 하나):
- 완료: 1~9 가 모두 있음이고, C-1 이 200, C-5 통과
- 진행 중: 자원이 일부 있고 실패 항목은 없음 → 남은 항목 번호를 순서대로 적는다
- 미착수: 그 계정에 dev 자원 0건
- 이상: 하나라도 실패, 또는 dev 자원이 기준 밖 설정(예: EKS 엔드포인트 0.0.0.0/0, 대상 없는 공개 SG)
공통 판정(한 줄씩):
- 운영 정상: C-3(D-22 기준) 4곳 결과
- 통합계정: C-4 — 신규 자원이 E-1 NS 레코드 건수뿐인가, 0/0 앱 그대로인가, ns ylab 은 D-26 상태 그대로 기록
- 마지막 줄에 "dev 이관 완료 고객: N / 4" 와 완료가 아닌 고객의 막힌 이유를 적는다.

[보고]
고객마다 짧게: 위 검토 표의 그 고객 열 + 판정 + 새 자원 수(cli-created.md).
최종: 현황판 세 표 + 위 검토 표 전체 + D-22 와이랩 관측 태그 + D-26 조사 결과 + 설계자 조치 대기 목록.
```
