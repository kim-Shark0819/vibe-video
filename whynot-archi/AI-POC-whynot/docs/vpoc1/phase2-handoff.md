# 2단계 인계 (Seedance 2.0)

PRD 12장 항목별 현재 상태와, 1단계에서 실측으로 알게 된 사실.

## PRD 12장 항목별 상태

| 항목 | 1단계가 남긴 것 | 2단계가 할 일 |
|---|---|---|
| provider 경계 | `app/src/vpoc/video.py` 의 `CAPS` dict + `submit(...)` · `poll(arn)` 두 함수. job 에 `provider` 를 적는다. 조립기가 `caps["maxPromptChars"]` 를 읽는다 | `CAPS["seedance-2.0"]` 항목과 구현을 더한다. 참조 이미지(`maxRefImages`)를 쓰는 조립 규칙을 `compose.py` 에 더한다 |
| 프로젝트 확정본 | `users/{owner}/video/{pid}/vpoc1/project.json` — 캐릭터 시트 전체 + `imageKey` + `imageSource` + `style` + `settingEn`/`settingKo` + `titleKo` | 다음 화 생성이 이것을 읽어 같은 캐릭터·배경·화풍으로 이어 간다 |
| 샷별 job 기록 | `…/plans/{planId}/jobs/{shotId}-{attempt}.json` — `invocationArn` · `mode` · `prompt` · `promptChars` · `outputPrefix` · `usd` | 모델별 job 스키마가 갈라지면 `provider` 로 분기한다 |
| 불변 완료 기록 | `…/plans/{planId}/final.json` — 샷·프롬프트·모델·파라미터·비용·출력 키·캐릭터·화풍·배경·입력 원문 | 회귀 비교의 기준으로 쓴다 |
| 샷 마지막 프레임 | **없다** (P2) | 다음 화 연결용으로 만들려면 완료 MP4 에서 마지막 프레임을 뽑아 저장한다. `imageio-ffmpeg` 가 이미 있다 |
| ECS 작업자 | **없다** (D-L07). Luma 는 비동기 API 라 조회 방식으로 충분했다 | Seedance 추론이 AWS 밖이므로 제출·폴링·결과 내려받기 작업자가 필요하다. ECS(Fargate)가 후보다 |
| 계약 기간 | AWS Marketplace 계약 2026-09-09~2026-10-09, 갱신 옵트아웃 상태 | **2단계 착수 전에 갱신 여부부터 결정한다** |
| API 키 | 없다 | 받으면 k8s Secret `seedance-api-key`(ns `whynot`) |
| 실사 얼굴 참조 | 확인하지 않았다 | ModelArk 공식 문서를 `docs/vendor/` 에 저장한 뒤 판단한다. 1단계 기본 화풍이 실사라 영향이 크다 |
| 데이터 전송 | 원본 웹툰 이미지를 외부로 보낸 적이 없다 | 서면 승인 전에는 BytePlus 로 보내지 않는다 |
| 3D 캐릭터 모델 · 체형 단계 | 1단계에서 뺐다. 체형은 `bodyKo`/`bodyEn` 로 시트에만 남긴다(캐릭터 이미지에만 쓰고 영상 프롬프트에는 넣지 않는다) | 일관성 설계에서 다시 볼지 결정한다 |

## 1단계 실측

| 항목 | 값 | 출처 |
|---|---|---|
| Luma Ray2 5초 540p 생성 시간 | **72초** (제출 → Completed) | Gate 0 C10 |
| 출력 크기 | 1,164,649 바이트 (1.16MB) | 같음 |
| 출력 Content-Type | `application/octet-stream` — presign 에서 `video/mp4` 로 덮어야 재생된다 | 같음 |
| **동시 요청 쿼터** | `On-demand model inference concurrent requests for Luma Ray V2` = **1** | Gate 0 C8 (service-quotas) |
| 프롬프트 길이 | 1,108자로 제출 성공. 조립 상한은 1,200자 | Gate 0 C10 |
| Claude Sonnet 4.5 Converse 왕복 | 1,641ms (ping, in 8 / out 5 토큰) | Gate 0 C3 |
| SD3.5 Large 1장 | `finish_reasons=[None]`, 성공 | Gate 0 C9 |
| presigned URL | **메서드에 묶인다.** GET 서명 URL 에 HEAD 를 보내면 403 SignatureDoesNotMatch | Gate 0 C10 (첫 판정 실패 원인) |
| 영상 버킷 라이프사이클 | `ExpireRawProviderOutput` 규칙이 걸려 있다 — provider 원본 출력이 약 2주 뒤 만료된다 | C10 응답의 `Expiration` 헤더 |
| EKS API 엔드포인트 | 사설이라 워크스테이션에서 `kubectl` 이 안 된다 (`dial tcp 100.10.6.238:443: i/o timeout`) | 2단계도 파드 안 실행에는 배스천이 필요하다 |
| 필터 실패 원문 | **관측하지 않았다.** Gate 0 의 실사 1인 텍스트 샷은 한 번에 통과했다 | 2인 샷·애니 화풍의 실패 원문은 Gate 2 에서 채운다 |

## 2단계가 먼저 읽어야 하는 파일

| 파일 | 왜 |
|---|---|
| `app/src/vpoc/video.py` | provider 경계. 여기만 늘리면 된다 |
| `app/src/vpoc/compose.py` | 조립 규칙과 코드 검사. 참조 이미지 규칙이 들어갈 자리 |
| `app/src/vpoc/ledger.py` | 비용 원장. 모델별 단가를 더한다 |
| `docs/vpoc1/review.md` 2-b 잔존 표 | 아직 남아 있는 구 영상 UI(`app.js`·`index.html`)와 인프라(`k8s-gpu/` 등). 후속 정리 대상 |
| `docs/vpoc1/infra-changes.md` §4 | Terraform 편입 대상 |

## 남은 위험

1. **영상 파일 보존.** 영상 버킷에 만료 규칙이 있어 완성본이 2주 뒤 사라질 수 있다. `final.json` 에
   키만 남으므로, 보존이 필요하면 완료 처리 때 주 버킷으로 복사하거나 접두사별 규칙을 나눠야 한다.
2. **동시 제출 1.** 샷 4개가 순차 제출이라 8~20분이 걸린다. 사용자 체감이 나쁘면 쿼터 인상 요청이
   필요하다(Service Quotas). 화면은 이미 대기 상태를 "동시 제출 한도로 대기 중"으로 보여 준다.
3. **구 영상 UI 잔존.** `app.js` 안의 구 영상 함수와 `index.html` 의 세 뷰 섹션이 남아 있다.
   접근 경로는 모두 끊었고 백엔드 라우트도 없지만, 코드가 남아 있는 한 다음 에이전트가 참조할
   위험이 있다. `check_vpoc.py` 가 새 코드에서의 사용은 막는다.
