import os

bind = f"{os.environ.get('LISTEN_HOST', '0.0.0.0')}:{os.environ.get('LISTEN_PORT', '8081')}"
workers = int(os.environ.get("GUNICORN_WORKERS", "4"))
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
