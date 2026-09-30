# vibe-video

와이낫 영상 기능 v2(vpoc2) 코드 보관 · 전달 저장소. 실제 실행 · 배포는 GitLab `awstech/ai` 의 `AI-POC-whynot` (dev: 통합계정).

| 문서 | 내용 |
|---|---|
| `docs/spec-v1.md` | 기능 명세 (설계자 결정 포함) |
| `docs/integration.md` | dev 에 넣는 방법 |
| `whynot-archi/RESUME.md` | 작업 재개 지점 |
| `whynot-archi/` | 와이낫 인수인계 자료 (vpoc1 문서 사본) |

## 흐름

① 명령 → ② AI 해석(명령 요소 체크리스트 · 15초 연출안) → ③ 캐릭터 이미지 확정 → ④ 5초 × 3샷 → 15초 합본 → ⑤ 리뷰(점수 · 요소별 반영 · 좋은 점 · 아쉬운 점)

## 로컬 목 모드 (모델 호출 없음, 비용 0)

```
pip install flask boto3 Pillow imageio-ffmpeg pytest
python tools/dev_server.py        # http://127.0.0.1:8765/vpoc2.html
python -m pytest -q tests
```
