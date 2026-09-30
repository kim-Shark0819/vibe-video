"""로컬 개발 서버 — 목 모드(모델 호출 없음, 비용 0)로 vpoc2 전체 흐름을 띄운다.

    python tools/dev_server.py            # http://127.0.0.1:8765/vpoc2.html
    VPOC2_MOCK=false ... 로 실제 AWS 를 부르려면 AWS 프로필과 버킷 설정이 필요하다 (docs/integration.md)

실제 whynot 앱에 들어갈 때는 이 파일을 쓰지 않는다. 인증은 앱의 require_auth 가 한다.
"""
from __future__ import annotations

import functools
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("VPOC2_ENABLED", "true")
os.environ.setdefault("VPOC2_MOCK", "true")
os.environ.setdefault("VPOC2_LOCAL_DIR", os.path.join(ROOT, ".vpoc2-local"))
sys.path.insert(0, os.path.join(ROOT, "AI-POC-whynot", "app", "src"))

from flask import Flask, send_from_directory  # noqa: E402

import vpoc2  # noqa: E402

PUBLIC = os.path.join(ROOT, "AI-POC-whynot", "frontend", "public")


def create_app() -> Flask:
    app = Flask(__name__)

    def require_auth(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            return fn(*a, **kw)

        return wrapper

    app.register_blueprint(vpoc2.create_blueprint(vpoc2.Vpoc2Dependencies(
        require_auth=require_auth, current_username=lambda: os.getenv("VPOC2_DEV_USER", "dev"))))

    @app.get("/")
    @app.get("/<path:name>")
    def static_file(name: str = "vpoc2.html"):
        return send_from_directory(PUBLIC, name)

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8765"))
    create_app().run("127.0.0.1", port, debug=False, threaded=True)
