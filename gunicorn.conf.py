import os

# nginx hace proxy_pass a un socket Unix dentro del directorio de la app:
#   proxy_pass http://unix:/home/deploy/apps/AppMant/AppMant.sock:/;
# Por eso el default es el socket y no TCP. GUNICORN_BIND lo sobrescribe,
# por ejemplo GUNICORN_BIND=0.0.0.0:8081 para probar por TCP.
#
# Ojo: este archivo lo lee gunicorn ANTES de que wsgi.py llame a
# load_dotenv(), asi que aca solo se ven las variables que pasa systemd,
# nunca las del .env.
_here = os.path.dirname(os.path.abspath(__file__))
bind = os.environ.get("GUNICORN_BIND") or f"unix:{os.path.join(_here, 'AppMant.sock')}"

# Se deja el umask por defecto de gunicorn (0), que crea el socket
# accesible para nginx sin depender de que www-data este en el grupo
# deploy. Para restringirlo: umask = 0o007 + usermod -aG deploy www-data.

workers = int(os.environ.get("GUNICORN_WORKERS", "4"))
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
