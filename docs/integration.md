# vpoc2 를 와이낫 dev 에 넣는 방법

대상: GitLab `awstech/ai` · 디렉터리 `AI-POC-whynot` · dev `https://dev-whynot.meta-clouds.com` · 통합계정 `730335451955` · ns `whynot`.
**이 작업은 GitLab 에 push 할 수 있는 로컬 세션에서 한다.** 이 저장소(GitHub)는 코드 보관 · 전달용이다.
배포 경로는 main 병합 → CI → ArgoCD `whynot-dev` 하나뿐이다 (`kubectl apply` · `deploy.ps1` 금지).

## 1. 파일 복사 (그대로)

| 이 저장소 | awstech/ai |
|---|---|
| `AI-POC-whynot/app/src/vpoc2/` (폴더 전체) | `AI-POC-whynot/app/src/vpoc2/` |
| `AI-POC-whynot/frontend/public/vpoc2.html` · `vpoc2.js` · `vpoc2.css` | `AI-POC-whynot/frontend/public/` 같은 이름 |

`tools/dev_server.py` · `tests/` 는 복사하지 않는다 (로컬 목 모드 전용).
새 의존성은 없다 — `boto3` · `flask` · `Pillow` · `imageio-ffmpeg` 는 이미 `requirements.txt` 에 있다 (vpoc1 review A6).

## 2. `server.py` — 등록 한 곳

vpoc1 블루프린트를 등록하는 곳(`vpoc.create_blueprint(...)` 바로 아래)에 추가한다.

```python
import vpoc2
app.register_blueprint(vpoc2.create_blueprint(vpoc2.Vpoc2Dependencies(
    require_auth=require_auth, current_username=lambda: g.username)))
```

`require_auth` 는 핸들러를 감싸는 기존 데코레이터, 사용자 id 는 `g.username` 이다 (vpoc1 review 2-c).

## 3. 설정 키

`deploy/config.env.example` (dev):

```
VPOC2_ENABLED=true
VPOC2_MOCK=false
VPOC2_RAW_ERRORS=true
VPOC2_MAIN_BUCKET=whynot-730335451955
VPOC2_MAIN_REGION=ap-northeast-2
VPOC2_VIDEO_BUCKET=whynot-video-730335451955-us-west-2
VPOC2_HQ_MONTHLY_LIMIT=1
```

`deploy/config.prod.env` (운영 오버레이 — 운영에서는 끈다):

```
VPOC2_ENABLED=false
VPOC2_RAW_ERRORS=false
VPOC2_VIDEO_BUCKET=
```

`k8s/workloads.yaml.tmpl` 의 `whynot-app` 컨테이너 env 에 같은 7개 키를 `${VAR}` 로 넣는다. **템플릿에 쓴 `${VAR}` 가 `config.env.example` 에 없으면 `deploy:whynot:dev` 가 실패한다** (`AI-POC-whynot/CLAUDE.md`).
모델 ID 는 코드 기본값(PRD 5.0 실측값)을 쓴다. 바꿀 때만 `VPOC2_TEXT_MODEL` · `VPOC2_IMAGE_MODEL` · `VPOC2_VIDEO_MODEL` 을 추가한다.

## 4. 권한 · 네트워크 — 새로 바꿀 것 없음 (확인만)

| 항목 | vpoc2 가 쓰는 것 | 이미 있는 근거 |
|---|---|---|
| Bedrock | Claude Sonnet 4.5(global) Converse · SD3.5 InvokeModel · Luma StartAsyncInvoke/GetAsyncInvoke | vpoc1 Gate 0 C5 allowed |
| 주 버킷 | `users/*` Get/Put (**나열 안 함**) | C5 allowed |
| 영상 버킷 | `users/*` Get/Put + `ListBucket`(prefix `users/`) | 인라인 정책 `vpoc1-luma` |
| CSP | 두 버킷 호스트 `img-src` · `media-src` | vpoc1 A9 (Report-Only) |

모든 키는 `users/{사용자}/video/_vpoc2/...` 와 `users/_vpoc2/...` 아래다.

## 5. 검사 · 배포 · 확인

1. 로컬: `python -X utf8 AI-POC-whynot/tools/check_vpoc.py` 통과 (vpoc2 에는 부록 G 구 식별자가 없다 — 이 저장소에서 grep 확인함)
2. 브랜치 push → MR → CI green → main 병합
3. `GET https://dev-whynot.meta-clouds.com/api/health` 의 `imageTag` 가 새 `ci-<sha8>` 인지 확인 (1~2분 지연)
4. `GET /api/vpoc2/meta` (로그인 없이) → **401** 이면 라우트가 등록된 것 (404 면 `VPOC2_ENABLED` 가 꺼져 있거나 등록 누락)
5. 브라우저: dev 메인에서 로그인 → **같은 탭** 주소창을 `https://dev-whynot.meta-clouds.com/vpoc2.html` 로 바꾼다
   (로그인 토큰이 탭별 `sessionStorage` 에 있어 새 탭에서는 401 이 난다)
6. 상단에 "목 모드" 배지가 **없어야** 한다

## 6. 되돌리기

`VPOC2_ENABLED=false` 로 바꿔 main 에 push 하면 `/api/vpoc2/*` 가 404 가 된다. vpoc1 과 다른 기능에는 영향이 없다 (파일 · 저장 경로 · 라우트가 모두 따로다).

## 7. 비용 (원장 `users/_vpoc2/ledger.json`)

| 항목 | 단가 |
|---|---|
| 15초 영상 540p | 3샷 × 3.75 = **11.25 USD** |
| 15초 영상 720p | 3샷 × 7.50 = 22.50 USD · **달마다 1편** (서버가 409 `HqMonthlyLimit` 로 막는다) |
| 캐릭터 이미지 | 0.08 USD/장 |
| Claude | 토큰 × (입력 3 / 출력 15 USD per 1M) |
