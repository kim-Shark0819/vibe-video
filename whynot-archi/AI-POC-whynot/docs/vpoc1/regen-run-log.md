# vpoc-regen 실행 기록

작업 트리 `C:\dev\ai\.worktrees\vpoc-regen` · 브랜치 `whynot/vpoc-regen` · 2026-09-23
정본 `docs/vpoc1/regen-plan.md` · 조사 `docs/vpoc1/regen-review.md`

---

## 병합과 배포

| 시각 (UTC) | 일 | 결과 |
|---|---|---|
| 22:4x | K-1 커밋 `e61cfc6` push | — |
| 23:0x | K-2 커밋 `ecbf392` push | 파이프라인 521 `check:whynot` **success** |
| 23:2x | K-3 커밋 `370c117` push | 파이프라인 522 **success** |
| 00:1x | MR !127 → main 병합 | merge commit **`af53864`** |
| 00:2x | 파이프라인 524 (main) | `check:whynot` · `probe` · `build:app` · `build:frontend` · `deploy:whynot:dev` **전부 success** · `deploy:whynot:prod` manual(실행 안 함) |
| 00:28 | ArgoCD `whynot-dev` 반영 | 이미지 태그 **`ci-af53864d`** |

`platform-drift` 는 이번에도 failed 다 — `allow_failure` 이고 vpoc1 작업 전 main 에서도 이미
failed 였다. 이번 변경으로 늘어난 drift 는 `k8s/workloads.yaml.tmpl` 하나이고 whynot 전용
env 추가라 다른 고객에 옮길 내용이 아니다.

## dev 확인 (HTTP 조회만)

| 확인 | 결과 |
|---|---|
| `/api/health` | 200 · `imageTag: ci-af53864d` |
| `/vpoc.js` | 200 · 71,343바이트 · `vpocRegenAttach`·`vpocRegenBusy`·`regenEnabled`·"이 샷 다시 만들기" 포함 |
| `/vpoc.css` | 200 · 14,112바이트 · `vpoc-regen-panel` 포함 |
| `POST /api/vpoc/…/run/revise` (인증 없이) | **401** — 라우트 등록됨 |
| `POST /api/vpoc/…/run/select` (인증 없이) | **401** |

## 자체 검사 (모델 호출 0건)

`python -X utf8 AI-POC-whynot/tools/check_vpoc.py` — 8건 전부 통과.

```
[ok] compileall app/src
[ok] 앱 임포트 스모크 — routes 71
[ok] node --check (4 files)
[ok] 잔존 검사 — 구 식별자 45종 0건
[ok] 조립기 자체 검사 7건
[ok] 멱등 키 검사 5건 (예: pl-20260922-de38-shot-01-1)
[ok] 재생성 검사 (a)옛 state (b)G2 격리 (c)select 영향 범위 (d)스위치 + 선행 조건
[ok] PlanView ④ 샷 키 — 기존 10개 유지 + 새 4개
```

`재생성 검사` 가 보는 것:

| 항목 | 내용 |
|---|---|
| (a) R9 | 새 필드가 전혀 없는 옛 계획을 읽어도 `versions` 가 1개(plan)로 보이고 `revision`·`regen` 이 null 이다. **읽기만 했는데 state 에 쓰이지 않는다**(마이그레이션 금지) |
| (b) G2 | `shot.regen` 이 submitted 인 동안 샷 본체의 `status`·`outputKey`·`attempt` 가 그대로다. `poll_targets` 가 regen 을 대상에 넣는다. `max_attempt` 가 regen attempt 를 센다 |
| (c) 영향 범위 | `select` 뒤 **다른 샷과 ③ 계획이 바이트 단위로 동일**하다. 선택 버전이 샷에 반영되고 합본이 `stale` 이 된다. 같은 attempt 로 다시 select 하면 되돌아간다 |
| (d) G6 | `REGEN_ENABLED=False` 면 `enabled()` 가 False 이고 `require_enabled` 가 **404** 를 던진다 |
| 선행 조건 | `FeedbackEmpty` · `FeedbackTooLong`(501자) · `RegenRunning` |

`PlanView ④ 샷 키` 는 소스에서 기존 10개 키(`id` `status` `attempt` `mode` `submittedAt`
`completedAt` `elapsedS` `videoUrl` `note` `error`)가 살아 있고 새 4개(`selectedAttempt`
`versions` `revision` `regen`)가 있는지 본다. 기존 키를 지우면 CI 가 실패한다.

## 실제 데이터로 확인 — revise (Claude 1회, 약 0.02 USD)

dev S3 의 **실제 계획** 상태를 읽어 `regen.do_revise` 를 한 번 돌렸다. Luma 는 부르지 않았고
`state.json` 에 쓰지 않았다.

| 항목 | 값 |
|---|---|
| 대상 | `pl_20260922_a2f2` / `shot_001` (완료된 4샷 계획) |
| 의견 | "표정을 이를 악물고 눈물을 참는 모습으로, 얼굴을 조금 더 가까이" |
| 수정안 id | `rev_33a22d7bdf83` |
| `reviewKo` | **null** — 조립기 검사 통과 |
| `promptChars` | **757** (상한 1,200) |
| `useKeyframe` | **false** — 2인 샷이라 자동으로 꺼졌다(5.2 규칙대로) |

검증된 것:

1. **부정형 → 긍정형 변환.** "눈물을 참는" 이 `clenched jaw and holding back tears` 로 나왔다.
   `no`/`not` 같은 부정어가 없다 — Luma 필터가 부정어를 제대로 못 읽는다는 전제를 지켰다.
2. **캐릭터 외형 불변.** 조립된 프롬프트의 캐릭터 문자열이 ②단계 `appearanceEn` 과 글자까지
   같다 — `middle-aged man with short black hair and angular strong jawline, …`.
   조립기가 캐릭터 문자열을 그대로 붙이는 1단계 일관성 장치가 깨지지 않았다.
3. **화풍 접두어 유지.** `2D anime-style animation, clean line art, cel shading, soft colors.`
   로 시작한다(이 계획은 애니 화풍이다).
4. **`locationEn` 이 배경 안에 있다.** `Modern Korean school office interior, daytime,
   fluorescent lighting` — `settingEn` 범위를 벗어나지 않았다.
5. **한글·이름·부정어·길이 검사 전부 통과** → `reviewKo` 가 null 이고 `promptEn` 이 조립됐다.

관찰(결함은 아니다): 의견에 인물을 지정하지 않아서 모델이 "이를 악물고 참는 표정" 을 두 인물 중
회장에게 붙였다. 입력이 모호했던 것이고, 화면의 수정안 비교에서 사용자가 보고 [의견 고쳐서 다시]
를 누를 수 있다.

## 실제 데이터로 확인 — regenerate 거부 경로 (과금 0)

같은 실제 계획 상태로 `regen.start_regenerate` 를 5가지 방식으로 거부시켰다. 모델을 부르지 않는다.

| 경우 | 오류 | state 불변 |
|---|---|---|
| R3 고급 편집에 한글("테스트 장면") | `PromptRejected` | ✓ |
| R3 고급 편집에 부정어("does not smile") | `PromptRejected` | ✓ |
| 금액 불일치(0.98 USD) | `CostMismatch` | ✓ |
| 수정안 id 불일치 | `RevisionMismatch` | ✓ |
| 이미 진행 중 | `RegenRunning` | ✓ |

**거부될 때 state 가 바이트 단위로 그대로다.** 즉 실패한 승인이 계획을 오염시키지 않는다.

## 아직 안 된 것 — 사용자 확인 필요

| 완료 기준 | 상태 |
|---|---|
| 1 그 샷만 새로 만들어지고 다른 샷이 그대로 | 자체 검사 (c)로 로직 확인. **실제 영상 생성은 사용자 확인 대기** |
| 2 재생성 중 기존 영상 재생 · ④ 상태 불변 | 자체 검사 (b)로 확인. 화면 동작은 사용자 확인 대기 |
| 3 새 버전 쓰기 / 이전 버전 유지 / 버전 목록에서 다시 고르기 | 자체 검사 (c)로 확인. 화면 동작은 사용자 확인 대기 |
| 4 새로고침 뒤 복원 | `state.json` 에 보관하므로 구조상 복원된다. 화면 확인 대기 |
| 5 원장에 재생성 1건 = 3.75 USD 정확히 한 번 | 멱등 키가 기존 규칙(`{planId}-{shotId}-{attempt}`)이라 중복되지 않는다. **실제 1건 확인 대기** |
| 6 기존 액션·키 그대로, CI green | **확인됨** (자체 검사 2건 + 파이프라인 524) |
| 7 스위치 끄면 404 | **확인됨** (자체 검사 (d)) |
| 8 오류 원문이 화면에 보인다 | **확인됨** (거부 경로 5건이 오류 봉투를 낸다. 화면은 기존 오류 상자를 쓴다) |

**유료 재생성 1건(3.75 USD)을 제가 돌리지 않았습니다.** dev 로그인 계정이 없고 EKS API 가
사설 엔드포인트라 `kubectl exec` 가 안 됩니다. 손으로 만든 스크립트로 사용자의 실제 계획
`state.json` 에 쓰는 것은 잘못 쓸 위험이 이득보다 커서 하지 않았습니다. 브라우저에서 확인해
주시는 쪽이 안전합니다.

원장 누계: **38.43 / 상한 60 USD** (revise 검증 Claude 1회 약 0.02 USD 포함).
재생성 1건에 3.75 USD 여유가 있습니다.
