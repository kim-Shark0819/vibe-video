# AI-POC-whynot 작업 안내

1. 정본은 `docs/vpoc1/PRD.md` 와 `docs/vpoc1/steps.md` 두 개다. 다른 문서와 충돌하면 이 둘이 우선한다.
2. 과거 영상 구현은 없는 것으로 취급한다. 이전 세션에서 본 구현·이름·흐름(개체 정리, 캐스트, 샷 분해, I2V 압축, Nova Reel, 6단계 등)을 기억에서 복원하거나 흉내 내지 않는다.
3. 백업 태그 `backup/whynot-video-v4-20260923` 을 checkout·diff·참조하지 않는다.
4. PRD 부록 G 의 구 식별자와 `docs/vpoc1/review.md` 의 잔존 항목을 새 코드에서 쓰지 않는다. `tools/check_vpoc.py` 가 이것을 강제한다.
5. 새 코드는 vpoc 이름공간만 쓴다 — 라우트 `/api/vpoc`, S3 `users/{owner}/video/{pid}/vpoc1/`, DOM `#vpoc-root`, CSS `vpoc-`. 플랫폼 파일(`gateway.py` `graph_store.py` `prompt_layers.py` `model_registry.py` `stitcher.py`)은 수정하지 않고 `server.py` 는 등록 한 곳만 바꾼다.

## 배포

`AI-POC-whynot` 개발 배포는 ArgoCD(`whynot-dev`)가 관리한다. 배포 경로는 `main` 푸시뿐이다.
`deploy/deploy.ps1` 로 배포하거나 배스천에서 `kubectl apply/edit/set/scale` 을 쓰지 않는다 —
selfHeal 이 몇 분 안에 되돌린다. 조회(`get`·`logs`·`describe`)는 괜찮다.

CI 렌더 원본은 `deploy/config.env.example`(+ `config.prod.env` 오버레이)다. 템플릿에 새
`${VAR}` 를 쓰면 반드시 `config.env.example` 에 키를 넣는다 — 없으면 `deploy:whynot:dev` 가 실패한다.

## 검사

CI `check:whynot` 은 `tools/check_vpoc.py` 하나만 부른다. 로컬에서도 같은 명령으로 돈다.

```
python -X utf8 AI-POC-whynot/tools/check_vpoc.py
```

정적 검사 통과는 완료 증거가 아니다. 완료 증거는 dev 브라우저에서 영상이 재생되는 것뿐이다.
