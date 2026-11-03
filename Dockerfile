# Imagen de la API de Lumen Optica (Django + DRF) servida con gunicorn.
FROM python:3.12-slim

# uv fijado a la misma version que se uso para generar uv.lock.
COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /uvx /bin/

# La imagen arranca segura por defecto (DEBUG apagado); compose.yaml
# lo sobreescribe para uso local. gunicorn escucha en 0.0.0.0:$PORT.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_DEBUG=0 \
    PORT=8000

WORKDIR /app

# Primero solo los manifiestos: esta capa queda en cache mientras
# no cambien las dependencias.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project

# Despues el codigo fuente y la instalacion del proyecto.
COPY . .
RUN uv sync --locked --no-dev

# La clave falsa solo existe en esta linea; sin DB_HOST usa SQLite
# y collectstatic no toca ninguna base de datos.
RUN DJANGO_SECRET_KEY=build-only-not-secret python manage.py collectstatic --noinput

RUN useradd --create-home --shell /usr/sbin/nologin app \
    && mkdir -p /app/media \
    && chown app:app /app/media
USER app

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--workers", "3", "--access-logfile", "-"]
