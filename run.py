import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        import subprocess, sys
        host = os.environ.get("LISTEN_HOST", "0.0.0.0")
        port = os.environ.get("LISTEN_PORT", "8081")
        workers = os.environ.get("GUNICORN_WORKERS", "4")
        bind = f"{host}:{port}"
        print(f"Iniciando servidor Gunicorn en http://{bind}")
        subprocess.run([
            sys.executable, "-m", "gunicorn",
            "--bind", bind,
            "--workers", workers,
            "run:app"
        ])
    else:
        print("Iniciando servidor de desarrollo en http://127.0.0.1:5000")
        app.run(host="127.0.0.1", port=5000, debug=True)
