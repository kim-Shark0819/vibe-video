# vpoc — ④영상 단계 "이 샷만 의견 반영해 다시 만들기" 추가 계획

> 기준: `AI-POC-whynot/docs/vpoc1/PRD.md`(vpoc1 PRD), main 최신. 대상 dev `https://dev-whynot.meta-clouds.com/`
> 이 문서가 이번 작업의 spec이다. Kiro spec(requirements/design/tasks)은 만들지 않는다.

---

## 0. 목표와 범위

완료된(또는 실패한) 샷 하나를 골라 **사용자 의견(한국어)** 을 적으면, AI가 그 샷의 장면 설명만 고친 수정안을 보여 주고, 사용자가 승인하면 **그 샷만** 새로 만든다. 새 영상이 나오면 사용자가 **새 버전 / 이전 버전 중 하나를 고른다.** 다른 샷·캐릭터·계획은 바뀌지 않는다.

| 구분 | 항목 |
|---|---|
| 포함 | 샷 카드의 [이 샷 다시 만들기] · 의견 입력(빠른 선택 칩 포함) · AI 수정안(전/후 비교, 영어 프롬프트 직접 수정 가능) · 비용 확인 후 재생성 · 진행 표시 · 버전 선택 · 프로젝트 보기·순차 재생·합본에 선택 버전 반영 |
| 제외 | 캐릭터 외형·화풍·배경 변경(전 샷에 영향 → ②단계에서 한다) · 샷 추가·순서 변경 · 여러 샷 동시 의견 한 번에 적용 · 영상 부분 편집(구간 자르기) · 모델 교체 |
| 한계(사용자에게 그대로 알린다) | 1단계 모델(Luma Ray2 텍스트→영상)은 캐릭터 얼굴을 완전히 고정하지 못한다. 다시 만들어도 얼굴이 다른 컷과 똑같아지는 것은 보장되지 않는다. 1인 샷은 "캐릭터 이미지로 시작하기"(키프레임)가 가능할 때 일관성이 조금 나아진다. 완전한 일관성은 2단계(Seedance) 목표다 |

---

## 1. 다른 코드에 영향을 주지 않기 위한 원칙

| # | 원칙 |
|---|---|
| G1 | **추가만 한다.** 기존 라우트·액션(`analyze` `prepare` `redraw` `generate` `retry` `stitch`)의 동작과 응답 키를 바꾸지 않는다. 새 액션 3개만 더한다 |
| G2 | **기존 샷 필드의 의미를 지킨다.** `shot.status` · `shot.videoUrl` · `shot.attempt` 는 항상 "지금 쓰는(선택된) 버전"을 뜻한다. 재생성 진행 상태는 새 하위 객체 `shot.regen` 에만 둔다. 그래서 재생성 중에도 기존 영상이 계속 재생되고 ④ 전체 상태(`steps["4"].status`)는 바뀌지 않는다 |
| G3 | **쓰기 규칙을 지킨다(PRD 6.4).** 조회(GET)는 `jobs/*.json` 만 쓴다. 새 버전으로 바꾸는 것은 사용자 동작(`select`)이 `state.json` 에 쓴다. 자동으로 바꾸지 않는다 |
| G4 | **불변 기록은 덮어쓰지 않는다.** `final.json` 은 그대로 두고, 버전을 바꿀 때마다 `finals/{UTC시각}.json` 을 새로 쓴다 |
| G5 | **기존 부품 재사용.** 제출·조회·원장·조립기·금지어 검사·오류 봉투·작업 스레드는 이미 있는 함수를 부른다. 새로 만들지 않는다. 플랫폼 파일(`gateway.py` `graph_store.py` `prompt_layers.py` `model_registry.py` `stitcher.py`)은 수정하지 않는다 |
| G6 | **기능 스위치.** `VPOC_REGEN_ENABLED`(기본 true, dev). false면 새 액션은 404, 화면 버튼은 숨김. 문제가 생기면 이 값만 끄면 이전 동작으로 돌아간다 |
| G7 | 새 코드는 vpoc 안에만: 서버 `app/src/vpoc/regen.py`(신규) + `routes.py` 의 액션 분기 3줄 + `store.py`/PlanView 직렬화에 필드 추가. 프론트는 `vpoc.js`·`vpoc.css` 만 |

---

## 2. 사용자 흐름

```
[샷 카드: 완료 또는 실패]
   └ [이 샷 다시 만들기]
        ↓
[의견 입력 패널]  칩: 표정 바꾸기 · 움직임 바꾸기 · 카메라 바꾸기 · 다른 컷과 얼굴 맞추기 · 배경 정리
   텍스트: "어떻게 바꾸고 싶은지 적어 주세요"  (예: 울기보다 이를 악물고 참는 표정, 얼굴을 조금 더 가까이)
   ☐ 캐릭터 이미지로 시작하기 (1인 샷 + 키프레임 가능할 때만 보이고 기본 체크)
   [수정안 만들기]  ← Claude 1회(무료에 가까움), 10~30초
        ↓
[수정안 비교]  현재 설명 | 수정안 설명 · 카메라 · (접힘) 영어 프롬프트 편집 · AI 메모
   [이대로 다시 만들기 · 3.75 USD]  [의견 고쳐서 다시]  [취소]
        ↓ 비용 확인 창
[샷 카드]  기존 영상은 그대로 재생 + 상단 띠 "새 버전 만드는 중 · 1:23 · 보통 2~5분"
        ↓ 완료
[버전 선택]  이전 버전 ▶ | 새 버전 ▶   [새 버전 쓰기] [이전 버전 유지]
        ↓ 선택
순차 재생·프로젝트 보기·합본이 선택 버전을 쓴다. 합본이 있었으면 "합본이 이전 버전입니다 [다시 이어 붙이기]"
```

버전은 샷마다 모두 남는다. 카드의 [버전 N개 ▾]에서 언제든 다른 버전을 다시 고를 수 있다.

---

## 3. 데이터 변경 (모두 추가 필드, 기존 필드 불변)

`state.json` 의 `steps["4"].shots[i]` 와 PlanView 응답에 더한다.

```json
{
  "id": "s3",
  "status": "completed",
  "attempt": 1,
  "videoUrl": "https://example.invalid/s3-1.mp4",
  "selectedAttempt": 1,
  "versions": [
    {"attempt": 1, "origin": "plan", "feedbackKo": null, "summaryKo": "…", "promptEn": "…", "mode": "text", "status": "completed", "videoUrl": "…", "createdAt": "2026-09-23T05:10:02Z"},
    {"attempt": 3, "origin": "regen", "feedbackKo": "울기보다 이를 악물고 참는 표정", "summaryKo": "…", "promptEn": "…", "mode": "keyframe", "status": "completed", "videoUrl": "…", "createdAt": "2026-09-23T06:02:11Z"}
  ],
  "revision": null,
  "regen": {"attempt": 3, "status": "completed", "elapsedS": 204, "videoUrl": "…", "error": null, "note": null}
}
```

| 필드 | 의미 | 없을 때(기존 데이터) |
|---|---|---|
| `selectedAttempt` | 지금 쓰는 버전 | `attempt` 값으로 간주 |
| `versions[]` | 이 샷의 모든 버전(재시도·E5 자동 재제출 포함, 실패도 기록) | 현재 샷 필드로 1개를 만들어 보여 준다 |
| `revision` | 승인 전 수정안 1개 | null |
| `regen` | 진행 중이거나 막 끝난 재생성 1건. 새 버전을 고르거나 유지를 누르면 null | null |

`attempt` 번호는 샷의 기존 최대 attempt + 1. `clientRequestToken` 은 기존 규칙 그대로라 중복 과금이 생기지 않는다. jobs 파일도 기존 규칙(`jobs/{shotId}-{attempt}.json`)과 출력 접두사 규칙을 그대로 쓴다.

---

## 4. API — 기존 `POST …/plans/<planId>/run/<action>` 에 액션 3개 추가

| 액션 | body | 선행 조건 | 동작 | 응답 |
|---|---|---|---|---|
| `revise` | `{shotId, feedbackKo, useKeyframe}` | 소유자 · 샷 status가 completed 또는 failed · `shot.regen` 이 진행 중이 아님 · 계획에 다른 작업 없음 · `feedbackKo` 1~500자 | 작업 스레드(202). Claude 1회로 그 샷만 고친 수정안을 만들어 `shot.revision` 에 저장 | 202 `{"ok":true,"task":"revise"}` |
| `regenerate` | `{shotId, revisionId, promptEn?, confirmUsd}` | `shot.revision.id == revisionId` · '검토 필요' 아님 · `confirmUsd` = 서버 계산 · 원장 여유 · `shot.regen` 진행 중 아님 | `promptEn` 이 오면 조립기 검사를 다시 통과해야 한다. 기존 제출 함수로 새 attempt 제출 | 200 `{"ok":true,"attempt":3,"status":"submitted"}` |
| `select` | `{shotId, attempt}` | 그 attempt가 `versions` 에 있고 completed | 선택 버전으로 갱신, `regen` 비움, 완료 기록 `finals/{UTC}.json`, Neptune 갱신, 합본 stale | PlanView |

"이전 버전 유지"는 `select` 에 현재 `selectedAttempt` 를 보내는 것과 같다.

오류 코드: 409 `RegenRunning` · `PreconditionFailed` · `CostMismatch` · `RevisionMismatch`, 400 `FeedbackEmpty`/`FeedbackTooLong`. (`BudgetExceeded` 는 상한을 없애면서 제거했다.)

조회(GET PlanView): 기존 샷 조회 로직이 `shot.regen.attempt` 의 job도 같은 규칙(샷당 10초 1회)으로 묻게 한다. queued 상태의 regen 제출도 기존 대기 제출 로직을 탄다.

---

## 5. 서버 규칙

### 5.1 revise — Claude 호출 (도구 `emit_shot_revision`, maxTokens 2,000)

입력: `story.settingKo/En` · 화풍 · 전체 캐릭터(`id, nameKo, handleEn, appearanceEn`) · 대상 샷의 현재 필드 · 바로 앞·뒤 샷의 `summaryKo` · `feedbackKo`.

| 규칙 | 내용 |
|---|---|
| 바꿔도 되는 것 | 이 샷의 `summaryKo` `cameraKo` `actionEn` `cameraEn` `locationEn`(`settingEn` 안에서) |
| 바꾸면 안 되는 것 | 캐릭터 `appearanceEn`, 화풍, 배경 전체, 다른 샷 |
| 인물 | 기본은 현재 샷의 `characters` 유지. 의견이 인물을 빼거나 더하라고 하면 0~2명 안에서 반영 |
| 외형·화풍 요청 | 적용하지 않고 `notesKo` 에 "외형·화풍은 ②단계에서 바꾸면 모든 샷에 적용됩니다" |
| "다른 컷과 얼굴 맞추기" | 프롬프트로 해결할 수 없다. `notesKo` 에 키프레임 안내를 적고, 동작·카메라를 얼굴이 잘 보이는 안정적인 구도로 바꾼다 |
| 표현 | 긍정형만(부정어 금지). 이름·한글(영어 필드)·실존 상표 금지. 예산은 PRD 부록 D-4 |
| 검사 | 기존 조립기 검사 함수 그대로. 위반이면 1회 재요청 → 그래도 위반이면 `reviewKo` 에 사유를 넣어 '검토 필요' |
| 결과 | 조립한 `promptEn`·`promptChars` 를 함께 저장. `useKeyframe` 은 5.2 조건을 만족할 때만 true |

도구 스키마:

```json
{
  "name": "emit_shot_revision",
  "description": "Return a revised version of exactly one shot.",
  "inputSchema": {
    "type": "object",
    "required": ["summaryKo", "cameraKo", "characters", "locationEn", "actionEn", "cameraEn", "notesKo"],
    "properties": {
      "summaryKo": {"type": "string"},
      "cameraKo": {"type": "string"},
      "characters": {"type": "array", "items": {"type": "string"}},
      "locationEn": {"type": "string"},
      "actionEn": {"type": "string"},
      "cameraEn": {"type": "string"},
      "notesKo": {"type": "string"}
    }
  }
}
```

### 5.2 regenerate

| 항목 | 규칙 |
|---|---|
| 키프레임 | 샷 인물이 정확히 1명 · 그 캐릭터 이미지 `source == "ai"` · 사용자가 체크. 2인 샷·사용자 이미지·웹툰 컷은 쓰지 않는다 |
| 실패 대체 | 키프레임 재생성이 Failed면 기존 E5 로직대로 텍스트 전용 1회 자동 재제출 |
| 비용 | 제출 성공 시점에 기존 원장 함수로 기록. 화면 금액은 서버 값 |
| 동시성 | 샷당 진행 중 regen 1개. 기존 `VPOC_MAX_INFLIGHT` 를 같이 쓴다 |
| 되돌리기와의 관계 | ③ 이전으로 되돌아가면 기존 규칙대로 ④가 stale 이 되고 `regen`·`revision` 도 버린다 |

### 5.3 select와 완료 기록

| 항목 | 규칙 |
|---|---|
| 완료 기록 | `final.json` 은 건드리지 않는다. `plans/{planId}/finals/{UTC시각}.json` 을 If-None-Match로 새로 쓴다 |
| 프로젝트 보기 | 가장 최근 완료 기록(`finals/` 최신 → 없으면 `final.json`)의 선택 버전을 쓴다 |
| 합본 | `selectedAttempt` 영상으로 만든다. 버전이 바뀌면 `final.status = "stale"` 과 [다시 이어 붙이기] |
| Neptune | `vpocFinalKey`·`vpocUpdatedAt` 만 갱신 |

---

## 6. 화면 (vpoc.js · vpoc.css)

| 위치 | 요소 |
|---|---|
| 샷 카드(완료·실패) | [이 샷 다시 만들기] · 버전 2개 이상이면 [버전 N개 ▾] · "버전 N 사용 중" 표시 |
| 의견 패널(카드 안에서 펼침, 모달 아님) | 칩 5개 · 텍스트칸(최대 500자, 글자 수) · 키프레임 체크박스(조건 만족 시만) · [수정안 만들기] · [닫기] |
| 수정안 비교 | 현재 / 수정안 두 칸 · AI 메모 · (접힘) 영어 프롬프트 편집 + 글자 수 · '검토 필요' 시 승인 잠금 · [이대로 다시 만들기 · 3.75 USD] [의견 고쳐서 다시] [취소] |
| 비용 확인 창 | "이 샷만 다시 만듭니다. 3.75 USD. 현재 누적 {spent} USD. 시작하면 취소할 수 없습니다. 기존 영상은 새 버전을 고르기 전까지 그대로 남습니다." |
| 진행 | 카드 상단 띠 "새 버전 만드는 중 · mm:ss · 보통 2~5분"(10분 넘으면 "평소보다 오래 걸려요") |
| 완료 | 이전/새 버전 나란히 재생 + [새 버전 쓰기] [이전 버전 유지] |
| 실패 | 오류 원문 상자 + [의견 고쳐서 다시] |
| 공통 | 기존 진행 표시·오류 상자·버튼 비활성 규칙 그대로. `canEdit` false면 다시 만들기·버전 선택 숨김 |
| 한계 안내(항상) | "지금 영상 모델은 캐릭터 얼굴을 완전히 고정하지 못해요. 다시 만들어도 다른 컷과 똑같아지지 않을 수 있어요." |

---

## 7. 예외 처리 사전 결정표

| # | 상황 | 처리 |
|---|---|---|
| R1 | revise 모델 출력이 스키마·금지어 위반 | 1회 재요청 → 실패면 수정안을 '검토 필요'로 저장(원문 사유), 승인 잠금 |
| R2 | revise 읽기 시간 초과·스로틀 | 재시도 없음, 오류 원문 + [다시 시도] |
| R3 | 고급 편집으로 프롬프트를 고침 | `regenerate` 에서 조립기 검사 재실행, 위반이면 400 원문 표시 |
| R4 | ~~원장 여유 부족~~ | **해당 없음.** 비용 상한을 없앴다 — 상한 없음, 누적 표시만 (2026-09-23 사용자 결정). 원장은 계속 기록한다 |
| R5 | 같은 샷에 regen 진행 중 다시 요청 | 409 `RegenRunning`, 버튼 잠금 |
| R6 | 키프레임 regen Failed | 기존 E5 대로 텍스트 전용 1회 자동 재제출 |
| R7 | 텍스트 regen Failed | 원문 표시, 이전 버전 유지, [의견 고쳐서 다시] |
| R8 | Throttling | 기존 대기(queued) 처리 |
| R9 | 기존 계획(필드 없는 state) | 3장 "없을 때" 규칙으로 읽는다. 마이그레이션 쓰기 없음 |
| R10 | 합본 기능이 없는 코드 | 합본 관련 부분 건너뜀 |
| R11 | 키프레임 제출 기능이 없는 코드 | 체크박스 숨김, 텍스트 전용만 |
| R12 | 계획이 ④ 완료 전 | 완료·실패한 샷만 다시 만들기 가능. 완료 기록은 계획이 완료 상태일 때만 |
| R13 | 한 문제에 20분 | 가장 작은 우회로 진행하고 `docs/vpoc1/regen-run-log.md` 에 적는다 |

---

## 8. 완료 기준

| # | 기준 |
|---|---|
| 1 | 샷 하나에 의견을 적고 승인하면 그 샷만 새로 만들어지고, 다른 샷의 영상·상태·프롬프트는 그대로다 |
| 2 | 재생성 중에도 기존 영상이 재생되고 ④ 전체 상태가 바뀌지 않는다 |
| 3 | 새 버전 쓰기 → 순차 재생·프로젝트 보기가 새 버전을 쓴다. 이전 버전 유지 → 그대로 |
| 4 | 새로고침 뒤에도 수정안·진행 상태·버전이 복원된다 |
| 5 | 원장에 재생성 1건 = 3.75 USD가 정확히 한 번 기록된다 |
| 6 | 기존 액션과 기존 PlanView 키가 그대로다(api-check.md 대조), CI green |
| 7 | `VPOC_REGEN_ENABLED=false` 면 버튼이 사라지고 새 액션은 404 |
| 8 | 오류 원문이 화면에 보인다(고급 편집에 한글을 넣어 확인 — 과금 없음) |
