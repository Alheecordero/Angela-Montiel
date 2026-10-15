#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/angelamontiel"
cd "$APP_DIR"

echo "==> Instalando dependencias Python"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Migraciones y archivos estáticos"
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "==> Reiniciando servicios"
systemctl restart gunicorn-angelamontiel.socket gunicorn-angelamontiel.service
systemctl reload nginx

echo "Despliegue completado."
