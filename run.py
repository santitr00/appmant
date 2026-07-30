import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        from waitress import serve
        host = os.environ.get("LISTEN_HOST", "192.168.1.54")
        port = int(os.environ.get("LISTEN_PORT", "8081"))
        print(f"Iniciando servidor Waitress en http://{host}:{port}")
        serve(app, host=host, port=port, threads=4)
    else:
        print("Iniciando servidor de desarrollo en http://127.0.0.1:5000")
        app.run(host="127.0.0.1", port=5000, debug=True)
