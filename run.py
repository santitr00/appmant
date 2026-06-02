import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    print("Iniciando servidor de desarrollo en http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
