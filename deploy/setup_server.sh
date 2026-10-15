#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/angelamontiel"
DB_NAME="angelamontiel"
DB_USER="angelamontiel"

echo "==> Creando directorio de la aplicación"
mkdir -p "$APP_DIR/public"
mkdir -p "$APP_DIR/media"

echo "==> Creando base de datos PostgreSQL (si no existe)"
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" | grep -q 1; then
    DB_PASS="$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)"
    sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQL
    echo "DATABASE_URL=postgres://${DB_USER}:${DB_PASS}@127.0.0.1:5432/${DB_NAME}" >> "${APP_DIR}/.env.credentials"
    chmod 600 "${APP_DIR}/.env.credentials"
    echo "Credenciales DB guardadas en ${APP_DIR}/.env.credentials"
else
    echo "Usuario DB ${DB_USER} ya existe — omitiendo creación"
fi

echo "==> Instalando unidades systemd"
cp deploy/systemd/gunicorn-angelamontiel.socket /etc/systemd/system/
cp deploy/systemd/gunicorn-angelamontiel.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable gunicorn-angelamontiel.socket

echo "==> Configurando nginx"
cp deploy/nginx/angelamontiel.conf /etc/nginx/sites-available/angelamontiel
ln -sf /etc/nginx/sites-available/angelamontiel /etc/nginx/sites-enabled/angelamontiel
nginx -t
systemctl reload nginx

echo "Setup base completado."
