#!/bin/bash
cd "$(dirname "$0")"

echo "Iniciando sitio Angela Montiel..."
echo ""
echo "  Sitio:  http://127.0.0.1:8000/"
echo "  Admin:  http://127.0.0.1:8000/admin/"
echo ""
echo "Presiona Ctrl+C para detener el servidor."
echo ""

python3 manage.py runserver 127.0.0.1:8000
