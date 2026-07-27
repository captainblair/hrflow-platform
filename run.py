import os

from app import create_app


app = create_app()


if __name__ == "__main__":
    # 0.0.0.0 so the app is reachable from outside a Docker container.
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
