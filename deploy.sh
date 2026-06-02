#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$APP_DIR/venv"
PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"
GUNICORN="$VENV/bin/gunicorn"

echo "==> Directorio: $APP_DIR"

# 1. Crear entorno virtual si no existe
if [ ! -f "$PYTHON" ]; then
    echo "==> Creando entorno virtual..."
    python3 -m venv "$VENV"
fi

# 2. Instalar dependencias
echo "==> Instalando dependencias..."
"$PIP" install --upgrade pip -q
"$PIP" install -r "$APP_DIR/requirements.txt" -q

# 3. Cargar variables de entorno de produccion
if [ -f "$APP_DIR/.env" ]; then
    set -a
    source "$APP_DIR/.env"
    set +a
fi

# 4. Aplicar migraciones
echo "==> Aplicando migraciones de base de datos..."
cd "$APP_DIR"
"$VENV/bin/flask" db upgrade

# 5. Iniciar Gunicorn
echo "==> Iniciando Gunicorn en ${LISTEN_HOST:-0.0.0.0}:${LISTEN_PORT:-8081}..."
exec "$GUNICORN" --config "$APP_DIR/gunicorn.conf.py" wsgi:app
