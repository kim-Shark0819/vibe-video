# vpoc1 전체 검토 (1단계)

작성 2026-09-23 · 작업 트리 `C:\dev\ai\.worktrees\vpoc1` · 브랜치 `whynot/vpoc1` · 기준 `origin/main` = `d62d020`
백업 태그 `backup/whynot-video-v4-20260923` → `d62d020` (원격 존재 확인: `git ls-remote --tags origin`)

---

## 2-a. 부록 F 가정 확인 (A1~A17)

| # | 가정 | 확인 결과 | 적용한 대체안 |
|---|---|---|---|
| A1 | 구 영상 라우트가 별도 모듈(`video_api.py`)로 등록된다 | **일치.** `server.py:12157` 에서 `video_api.create_blueprint(VideoDependencies(...))`, `server.py:12192` 에서 `app.register_blueprint`. `url_prefix="/api/video"` | vpoc 도 같은 방식을 따른다 — `vpoc.create_blueprint(vpoc.VpocDependencies(...))`, `url_prefix="/api/vpoc"`. 등록 지점은 `server.py` 맨 아래 한 곳 |
| A2 | 인증 데코레이터 · 가시성 · 소유자 판정 함수가 있다 | **일치.** `require_auth`(`server.py:422` 원본), 로그인 사용자 id 는 `g.username` 문자열. `can_read_project`(`server.py:953`) / `can_write_project`(`server.py:959`) — 둘 다 `g` 의존 | 주입으로 받는다. vpoc 는 `g` 를 직접 읽지 않고 `current_username()` 람다를 받는다 |
| A3 | gateway 로 Claude·SD3.5 를 모델 ID 지정해 부를 수 있다 | **부분 일치.** `gateway.converse(model_id, region, ...)` 는 모델 ID 를 직접 받는다. 그러나 이미지는 `gateway.invoke_image(model: dict, ...)` 로 카탈로그 엔트리 dict 를 요구하고, 실사용 경계는 `video_callers.py`(삭제 대상)였다. purpose 등록은 `prompt_layers.register_roles` 가 필요 | **E12 적용.** vpoc 안에서 boto3 `bedrock-runtime` 을 직접 부른다. `gateway.py`·`prompt_layers.py` 를 수정하지 않는다. 사용량은 vpoc 원장(`ledger.py`)이 센다 |
| A4 | 앱 IRSA 가 주 버킷 `users/*` 읽기·쓰기를 허용한다 | **일치.** Gate 0 C5 simulate 결과 `s3:PutObject`·`s3:GetObject` on `whynot-730335451955/users/_vpoc1/x` = allowed | 모든 키를 `users/{owner}/video/{pid}/vpoc1/` 아래에 둔다 |
| A5 | us-west-2 에 whynot 영상 버킷이 **없다** | **불일치.** 이미 있다 — `whynot-video-730335451955-us-west-2`(`config.env.example:93` `S3_VIDEO_BUCKET`), `get-bucket-location` = us-west-2, 기본 암호화 SSE-S3(AES256), 버킷 정책은 `DenyInsecureTransport` 하나 | **버킷을 새로 만들지 않았다.** E1 미발동. 기존 버킷의 `users/` 아래를 쓴다. D-L02(a)는 사용하지 않았다 |
| A6 | 앱 이미지에 Pillow · imageio-ffmpeg 가 있다 | **일치.** `requirements.txt` — `Pillow==11.3.0`, `imageio-ffmpeg==0.6.0`, `boto3==1.40.2` | 추가 의존성 없음. 합본(P1)은 `stitcher.concat` 을 그대로 쓴다 |
| A7 | 프론트에 토큰 저장 키 · API 헬퍼가 있다 | **일치.** `sessionStorage["toon-change-ai-pj:token"]`(`app.js:79`), 공통 `api()`(`app.js:400`) | `vpoc.js` 는 같은 토큰 키를 읽고 **자체 fetch 래퍼**를 쓴다(app.js 전역에 의존하지 않는다) |
| A8 | 영상 화면 진입이 트랙 선택 · 프로젝트 카드 · `/video` 세 곳이다 | **일치.** 세 경로 모두 `navigate("videoGen")` 으로 수렴한다 — `dispatchProject`(`app.js:1581`), `whynotOpenVideoGen`(`app.js:6073`), ROUTES `{view:"videoGen", path:"/video"}` | `videoGen` 뷰 이름을 그대로 유지하고 `switchView` 의 진입 훅 한 줄만 `window.vpoc.mount(projectId)` 로 바꿨다. 세 경로가 모두 자동으로 새 화면으로 간다 |
| A9 | CSP 가 `nginx.conf` 에 있다 | **일치, 단 Report-Only.** `map $host $toon_csp`(28행) + `add_header Content-Security-Policy-Report-Only` 3곳 | 두 버킷 호스트를 `img-src`·`media-src` 에 추가했다. `media-src` 에서 광범위한 `https:` 를 걷어내고 두 호스트만 남겼다. `connect-src 'self'` 는 유지 — 영상은 `<video src>` 로 재생하고 fetch 로 읽지 않는다 |
| A10 | 정적 자산 버전 치환이 프론트 Dockerfile 에서 일어난다 | **일치.** `sed` 대상이 `index.html`·`app.js` 두 개였다 | `vpoc-smoke.html` 을 치환 대상에 추가했다. `vpoc.js`·`vpoc.css` 는 `index.html` 의 `?v=` 쿼리로 버전이 붙으므로 파일 자체 치환은 필요 없다 |
| A11 | whynot dev 설정이 `render.py` 에 있다 | **부분 불일치.** `render.py` 는 치환기이고 값의 정본은 `deploy/config.env.example`(+ `config.prod.env` 오버레이)다. `config.env` 는 gitignore 이며 CI 가 만든다 | 새 키 18개를 `config.env.example` 에 넣고 `k8s/workloads.yaml.tmpl` 에 env 로 주입했다. 운영 오버레이에는 `VPOC_ENABLED=false`·`VPOC_RAW_ERRORS=false`·`VPOC_SMOKE_ENABLED=false`·`VPOC_VIDEO_BUCKET=` 을 넣었다. dev/prod 양쪽 `render.py` 실행으로 미해결 `${VAR}` 0건을 확인했다 |
| A12 | gunicorn 타임아웃 ≥ 60초 | **일치(경계값).** `app/Dockerfile:41` — `--workers 2 --threads 4 --timeout 60` | 모델 호출은 전부 202 + 조회. 동기 요청은 저장·조회·합본뿐이다. 합본은 60초를 넘을 수 있어 완료 샷을 내려받아 stream copy 로 잇는다(재인코딩은 실패 시 fallback) |
| A13 | 업로드 크기 제한 ≥ 10MB | **확인 불가 → 앱 한도로 통일.** `nginx.conf` 에 `client_max_body_size` 가 없고(이 nginx 는 API 를 프록시하지 않는다) 앱은 `app.config["MAX_CONTENT_LENGTH"] = MAX_VIDEO_BYTES` 를 쓴다. ALB/Ingress 한도는 조회하지 않았다 | 화면에서 10MB 초과를 먼저 거절하고(E13) 서버도 413 `FileTooLarge` 로 막는다 |
| A14 | `.kiro/` 가 저장소 루트에 있고 고객별 파일이 섞여 있다 | **일치.** `specs/` 11개 중 10개가 구 영상 spec, `steering/` 13개 중 3개가 영상 문서. `hooks/`·`out/` 은 **없다** | 구 영상 spec 10개와 steering 3개를 지웠다. `09-project-track-selection`(트랙 선택 = 플랫폼)은 남겼다. 새 steering `whynot-vpoc1.md` 하나를 넣었다 |
| A15 | CI `check:whynot` 가 검사기를 호출하고 build 가 그 뒤에 온다 | **일치.** `check:whynot`(stage check, needs 없음) → `build:whynot:app`/`build:whynot:frontend` → `deploy:whynot:dev`(needs 세 개) | job 이름·stage·needs 를 유지하고 script 의 검사기 14줄을 `check_vpoc.py` 한 줄로 바꿨다. `changes` 목록에서 `AI-POC/app/src/story_video/**` 와 `story_contract.py` 를 뺐다(그 경로를 더 이상 쓰지 않는다) |
| A16 | `stitcher.py` 는 플랫폼 공용이다 | **부분 불일치.** 소비자가 전부 영상 모듈이었다. 제거 후 `server.py:40` 임포트만 남는다 | 지시대로 **지우지 않고 잔존**으로 두고 vpoc 합본(P1)이 쓴다. 입력은 로컬 파일 경로다(S3 키가 아니다) — `concat(clip_paths, output_path)` |
| A17 | boto3 가 S3 조건부 쓰기(IfMatch · IfNoneMatch)를 지원한다 | **일치.** `boto3==1.40.2`(로컬 확인 1.40.25) 가 `put_object(IfMatch=, IfNoneMatch=)` 를 받는다 | 조건부 쓰기를 쓴다. 지원하지 않는 버전에서는 `ParamValidationError`/`NotImplemented` 를 잡아 한 번만 판정하고 이후 조건 없이 쓴다(`store.py` `_CONDITIONAL_WRITES`) |

### 가정 외에 실측으로 바뀐 것

| 발견 | 값 | 영향 |
|---|---|---|
| Luma Ray2 on-demand **동시 요청 쿼터 = 1** (Gate 0 C8, service-quotas) | `"On-demand model inference concurrent requests for Luma Ray V2"` = 1.0 | PRD 는 `VPOC_MAX_INFLIGHT=2`(최대 4)를 제안했지만 **1 로 내렸다.** 2 로 두면 두 번째 제출이 ThrottlingException 이 되고 E4 로 queued 로 되돌아가며 제출이 헛돈다. 4샷은 순차 제출이라 대략 4×(2~5분) = 8~20분이 걸린다 |
| presigned URL 은 **메서드에 묶인다** | `generate_presigned_url("get_object")` 로 만든 URL 에 HEAD 를 보내면 403 SignatureDoesNotMatch | 사전 점검의 검사 방식을 GET + `Range: bytes=0-0` 으로 바꿨다. 브라우저 `<video>` 도 GET 이라 실제 재생에는 문제가 없었다 |
| Luma 출력의 Content-Type | `application/octet-stream` (Bedrock 이 그렇게 쓴다) | presign 에 `ResponseContentType=video/mp4` 를 넣어 브라우저가 재생하게 한다 |
| EKS API 엔드포인트가 사설이다 | `dial tcp 100.10.6.238:443: i/o timeout` | 워크스테이션에서 `kubectl exec` 가 불가능하다. 유료 점검(C9·C10)을 사용자 프로필(`ai-poc-hub`)로 돌렸고 **앱 역할 판정은 C5(IAM simulate)로 대신했다** |
| `project_tracks.py` 가 `video_scene` 그래프 라벨을 조회하고 있었다 | `metadata_for()` 의 `OPTIONAL MATCH (p)-[:has_video_scene]->(s:video_scene {...})` | 그 라벨을 쓰는 코드가 사라져 항상 0을 돌려줬을 것이다. 쿼리를 `p.vpocStatus` 기반으로 바꿨다(3줄). 메인 목록의 영상 배지가 다시 동작한다 |
| `project_tracks.install(...)` 이 `video_store.HostVideoStore` 를 `command_store` 로 받고 있었다 | 트랙 선택 기록을 구 `project-state.json` 에 남겼다 | `server.py` 에 `_VpocTrackCommandStore` 를 두어 기록 위치를 `users/{owner}/video/{pid}/vpoc1/track-commands.json` 으로 옮겼다. 트랙 선택(플랫폼 기능)이 그대로 동작한다 |

---

## 2-b. 구 영상 기능 목록과 조치

### 삭제 — 백엔드 모듈 (영상 전용)

| 대상 | 판정 근거 |
|---|---|
| `app/src/video_api.py` (2,961줄, 51개 라우트) | 6단계 영상 흐름의 단일 진입점 |
| `app/src/story_video/` (21개 파일) | 6단계 흐름 코어 |
| `app/src/scene_video/` (하위 `cuts/`·`modeling/`·`providers/`·`render/` 포함) | Seedance/Nova Reel/Luma provider, 컷 분해, 키프레임 |
| `app/src/roles/video/` (6개 파일) | 영상 역할 프롬프트 |
| `app/src/fixtures/video/` | 영상 고정 자료 |
| `video_callers.py` `video_cuts.py` `video_graph.py` `video_jobs.py` `video_purposes.py` `video_records.py` `video_spec.py` `video_stitcher_mock.py` `video_store.py` `video_types.py` `wan_client.py` | 영상 전용 |
| `story_generate.py` `story_i2v.py` `story_clips.py` `story_people.py` `story_steps.py` `story_assemble.py` `story_characters.py` `story_failures.py` `story_host.py` `story_results.py` `story_state.py` `story_text_input.py` `story_understand.py` | 영상 전용 |
| `character_curator.py` `mock_media.py` `seedance_client.py`(top-level 고아) | import 하는 곳이 없거나 영상 전용 |

### 삭제 — `server.py` 부분 삭제

`ast` 로 최상위 노드 경계를 잡아 (1) 영상 라우트 61개 (2) 삭제된 이름을 참조하는 최상위 정의를
고정점까지 반복 제거했다. **12,253줄 → 6,780줄 (5,473줄 제거).**

- 영상 import: `video_prompt`(잔존, 아래 참고) 외 `wan_client` `video_api` `video_jobs` `video_store`, `scene_video` 계열 20줄
- 라우트: `/api/videos*` `/api/v2/video/*` `/api/storyboards*` `/api/scenes*` `/api/scene-productions*` `/api/scene-memories*` `/api/characters*` `/api/character-tags*` `/api/video/readiness`
- 헬퍼: `story_model_mode` `video_output_buckets/exists/read` `adopt_wan_job` `run_wan_job` `watch_wan_job` `build_generation_manifest` `_production_*` `_scene_*` `_run_scene_generation` `_assemble_scene` `video_readiness` 등 42개
- `LEGACY_VIDEO_WRITE_MODE` + `_retired_video_write_path()` + `require_auth` 안의 차단 호출 (대상 라우트가 전부 사라졌다)
- 블루프린트 등록과 durable runner 기동

`project_tracks.install(...)` 은 `_project_command_store` 참조 때문에 함께 쓸려 나갔고 **복원했다**(위 표 참고).

### 삭제 — 프론트엔드

| 대상 | 비고 |
|---|---|
| `scene.js` `scene-cuts.js` `story-app.js`(181KB) `story-characters.js` `story-text-input.js` `story-text-input.css` `video-folder.js` `production.js` | 영상 전용 스크립트 8개 |
| `index.html` 의 해당 `<script>`·`<link>` 태그 8개 | `vpoc.css`·`vpoc.js` 두 줄로 대체 |
| `index.html` 의 `#videoGenView` 본문 202줄 | `<div id="vpoc-root">` 로 대체 |
| `app.js` 진입 배선 | ROUTES 의 `sceneProduction` 제거, 뷰 제목 3개 제거, `switchView` 의 onEnter 훅 4줄 → `window.vpoc.mount()` 한 줄, `sendProjectTo` 의 `sceneVideo` 분기 제거, `whynotVideoFolder.render` 호출 제거, `renderWorkingProject` 의 showOn 목록 정리 |

### 삭제 — 검사기 · spec · 문서

| 대상 | 개수 |
|---|---|
| `tools/` 의 구 검사기·스모크·측정 도구 | 36개 (전부) |
| `tests/` | 디렉터리 전체 |
| `.kiro/specs/` 구 영상 spec | 10개 디렉터리 |
| `.kiro/steering/` `scene-video-rules.md` `character-modeling.md` `genre-bl.md` | 3개 |
| `docs/prd.md` `prd2.md` `prd3.md` `prd-v1.3.md` `prd2-v1.3.md` `Whynot_*` 2개 `seedance-spec.md` `whynot-video-rebuild-design.md` `phase10~22.md` | 20개 |
| `docs/gpu-video/` `docs/plans/` `docs/story-dev-beta_overlay/` `docs/text-input-extension/` `docs/run-log/story-video-rebuild/` `docs/run-log/story-timeout-characters/` `docs/run-log/gpu-*.md` | 7개 경로 |
| `deploy/verify/` 의 영상 검증 스크립트 | 8개 |

**지우지 않은 것**: S3·Neptune 데이터, `docs/vendor/`, `docs/구조분석.md`(PRD 가 참조하는 필터 실측 근거), `docs/AI-POC_history.md`, 다른 고객 디렉터리(`AI-POC-keyeast` 등)와 그 CI job, `.kiro/specs/09-project-track-selection`.

### 부분 삭제 — 플랫폼 파일 (카탈로그 항목만)

| 파일 | 조치 |
|---|---|
| `app/src/providers.py` | `NovaReelAdapter` 클래스와 어댑터 등록 1줄 제거. `LumaRayAdapter` 는 그대로 |
| `app/src/model_capabilities.py` | `amazon.nova-reel-v1:0`·`v1:1` 항목 → `luma.ray-v2:0`(540p 0.75 USD/초) |
| `app/src/model_registry.py` | `_PROVIDER_BY_MODEL_PREFIX` 에서 `("amazon.nova-reel", ...)` 제거 |
| `k8s/model-catalog.yaml.tmpl` | `nova-reel` 모델 엔트리 → `luma-ray2`(isDefault) |
| `k8s/workloads.yaml.tmpl` | `VIDEO_GEN_URL`(삭제된 `wan_client` 전용) 제거, vpoc env 18개 추가 |
| `app/src/project_tracks.py` | `metadata_for()` 쿼리를 `video_scene` → `p.vpocStatus` 로, `_metadata_view()` 에 `vpocStatus`·`vpocPlanId` 추가 |

### 잔존 — 사유 기록

| 대상 | 사유 |
|---|---|
| `app/src/video_prompt.py` | **플랫폼 파일이 참조한다.** `documents.py:16`(콘티 문서 생성이 `assemble_shot`·`CAMERA_MOVES`·`SHOT_TYPES` 를 쓴다)와 `prompt_layers.py:215-365`(관리자 프롬프트 화면이 심볼을 문자열로 참조). E20 에 따라 import 한 줄 이상의 리팩터링은 하지 않았다. 모델을 부르지 않는 순수 조립 모듈이다. 부록 G 목록에 없다 |
| `app/src/stitcher.py` | PRD 지시대로 지우지 않는다. vpoc 합본(P1)이 쓴다 |
| `app/src/documents.py` `prompt_layers.py` `graph_store.py` | 플랫폼 파일. `graph_store.py` 는 `video_scene`·`video_job`·`video_rating` 쿼리를 190건 품고 있다 — 제거에는 대규모 리팩터링이 필요하고 **그래프 데이터를 지우지 말라는 제약**과도 맞물린다. 부록 G 는 이 라벨을 "새 코드에서만" 검사하므로 `check_vpoc.py` 도 그렇게 한다 |
| `frontend/public/app.js` 안의 구 영상 UI 함수 (약 2,500줄) · `index.html` 의 `#videoNewView`·`#sceneVideoView`·`#sceneProductionView` 섹션 · `styles.css` | **E20 적용.** `app.js` 는 로그인·메인 목록·프로젝트 상세·스튜디오·이미지 스튜디오가 한 파일에 들어 있는 플랫폼 파일이다. 구 영상 UI 함수 260개 id 중 `wan*`·`sb*`·`sequence*`·`videoStyle` 등이 **optional chaining 없이** DOM 을 읽어서, 마크업만 지우면 초기화 중에 앱 전체가 죽는다. 4시간 한도 안에서 안전하게 떼어낼 방법이 없었다. 대신 **접근 경로를 모두 끊었다** — ROUTES·뷰 제목·진입 훅·트랙 분기에서 제거해 사용자가 도달할 수 없고, 백엔드 라우트가 전부 사라져 호출해도 404 다. 후속 정리 대상으로 남긴다 |
| `k8s-gpu/` `video-worker/` `terraform/hub/40-video-gpu` `terraform/modules/video_*` `infra/app-s3-policy-dual-video.json.tmpl` | 영상 전용 인프라. 삭제는 Terraform·ArgoCD 절차가 따로 필요하고 이번 범위(D-L02) 밖이다 |
| `deploy/config.env.example` 의 `SCENE_VIDEO_*` `VIDEO_OUTPUT_REGION` `ARK_*` `WAN_*` 등 | 템플릿(`k8s-gpu/`)이 아직 참조한다. 키를 지우면 `render.py` 가 실패한다 |

---

## 2-c. 새 코드가 쓰는 기존 부품

| 필요한 것 | 실제 이름 · 위치 | vpoc 에서 쓰는 방법 |
|---|---|---|
| 인증 데코레이터 | `require_auth(handler)` — `server.py`. 사용자 id 는 `g.username`(문자열), 역할 `g.role` | `VpocDependencies.require_auth` 로 주입 |
| 현재 사용자 | `g.username` | `current_username=lambda: g.username` |
| 프로젝트 조회 | `project_tracks.GraphProjectTrackRepository.get_project(project_id)` — `graph_store.get_project` + 트랙 정보 | `get_project` 로 주입 |
| 가시성 · 소유자 | `can_read_project(project)` / `can_write_project(project)` — `server.py`. 소유자 키는 `project["owner"]`, 가시성은 `visibility in {"shared","private"}` | 주입. 저장 경로의 주인은 `project["owner"]`(보는 사람이 아니다) |
| 프로젝트 정점 id 속성 | `p.id` | `MATCH (p:project {id: $id})` |
| S3 주 버킷 | 환경변수 `S3_BUCKET` = `whynot-730335451955` | `vpoc/settings.MAIN_BUCKET`. 클라이언트는 vpoc 가 직접 만든다(리전별 캐시, `s3v4` + virtual addressing) |
| presign | `server.presign(bucket, key, region, expires, content_type)` 가 있지만 `g` 와 무관하다 | vpoc 는 `store.STORE.presign()` 을 자체로 가진다 — 버킷마다 그 리전 클라이언트를 쓰고 `ResponseContentType` 을 넣는다 |
| Neptune 쿼리 | `graph_store.run(query, parameters) -> list[dict]` (openCypher 전용, Gremlin 없음) | `graph_run` 으로 주입. `project` 정점 속성 5개만 SET |
| 합본 | `stitcher.concat(clip_paths: list[str], output_path: str) -> str` (**로컬 파일 경로**) | 완료 샷을 임시 디렉터리로 내려받아 잇는다 |
| Claude · 이미지 · 영상 호출 | `gateway.converse` / `gateway.invoke_image(model: dict, ...)` / `gateway.start_video` | **쓰지 않는다(E12).** vpoc 가 boto3 `bedrock-runtime` 을 직접 부른다. purpose 등록(`prompt_layers.register_roles`)도 하지 않는다 |
| 프론트 토큰 | `sessionStorage["toon-change-ai-pj:token"]` | `vpoc.js`·`vpoc-smoke.js` 가 같은 키를 읽는다 |
| 프론트 API 헬퍼 | `api(path, options)` — `app.js:400` | 쓰지 않는다. `vpoc.js` 가 자체 fetch 래퍼를 가진다 |
| 영상 화면 진입 | `navigate("videoGen")` 세 경로 → `switchView` 의 진입 훅 | `window.vpoc.mount(state.currentProject?.id)` |
| CSP | `frontend/nginx.conf` `map $host $toon_csp`(28행), **Report-Only** | 두 버킷 호스트를 `img-src`·`media-src` 에 추가 |
| ASSET_VERSION | `frontend/Dockerfile` 의 `sed` (실패 시 빌드 중단) | `vpoc-smoke.html` 을 대상에 추가 |
| dev 설정 | `deploy/config.env.example` + `config.prod.env` → `deploy/render.py` → `k8s/*.tmpl` | 새 키 18개 추가 |
| 앱 Deployment · SA · IRSA | Deployment `whynot-app`, SA `whynot-app`, 역할 ARN `${IAM_APP_ROLE_ARN}` = `arn:aws:iam::730335451955:role/whynot-app-role`, ns `whynot` | 인라인 정책 `vpoc1-luma` 를 이 역할에 붙였다 |
| gunicorn | `--workers 2 --threads 4 --timeout 60` | 긴 작업은 202 + 배경 스레드 |
| CI | `check:whynot`(stage check) → `build:whynot:app`·`build:whynot:frontend` → `deploy:whynot:dev`(ArgoCD `whynot-dev`) | script 를 `check_vpoc.py` 한 줄로 교체 |
