#!/bin/sh
set -e

python manage.py migrate --noinput

# exec: gunicorn reemplaza al shell y queda como PID 1, asi recibe
# SIGTERM directamente en `docker compose down`.
exec "$@"
