# Ejecutar Lumen Óptica con Docker Compose

La API corre en dos contenedores definidos en `compose.yaml`:

| Servicio | Imagen | Rol |
|---|---|---|
| `web` | construida con el `Dockerfile` (`build: .`) | Django + DRF servido por gunicorn; WhiteNoise sirve los estáticos |
| `db` | `postgres:15` | Base de datos PostgreSQL, datos en el volumen `postgres_data` |

Sin Docker el proyecto sigue funcionando igual que antes (`uv run python manage.py runserver`, SQLite, sin `.env`).

## Requisitos

- Docker Engine con el plugin Compose v2 (`docker compose version`) y buildx (`docker buildx version`).
- Puerto `8000` libre en la máquina.

## Primer arranque

```bash
cp .env.example .env          # .env está en .gitignore: nunca se sube a GitHub
# editar .env y cambiar POSTGRES_PASSWORD

docker compose config         # valida el archivo y muestra las variables ya interpoladas
docker compose up -d --build  # construye la imagen y levanta db + web en segundo plano
docker compose ps             # ambos servicios deben quedar "healthy"
docker compose logs -f web    # migraciones + logs de gunicorn (Ctrl+C para salir)
```

Al arrancar, `web` espera a que `db` esté sano (`depends_on: condition: service_healthy`), aplica las migraciones (`docker/entrypoint.sh`) y levanta gunicorn.

URLs: <http://127.0.0.1:8000/> · `/api/` · `/api/docs/` (Swagger) · `/api/redoc/` · `/admin/`

## Comandos útiles

```bash
docker compose exec web python manage.py createsuperuser   # crear admin
docker compose exec web python manage.py test              # tests contra PostgreSQL
docker compose down       # detiene y borra contenedores; los datos QUEDAN en los volúmenes
docker compose down -v    # además borra los volúmenes: SE PIERDE la base y las imágenes subidas
```

## Variables de entorno

Se definen en `.env` (ver `.env.example`). Compose las interpola en `compose.yaml`.

| Variable | Default en Compose | Para qué sirve |
|---|---|---|
| `POSTGRES_PASSWORD` | **obligatoria** (`docker compose config` falla sin ella) | Contraseña de PostgreSQL; la usan la imagen `postgres` y Django |
| `POSTGRES_DB` | `lumen_optica` | Nombre de la base |
| `POSTGRES_USER` | `lumen` | Usuario de la base |
| `DJANGO_DEBUG` | `1` | `0` = modo producción (la imagen sola arranca con `0`) |
| `DJANGO_SECRET_KEY` | vacío | Obligatoria con `DJANGO_DEBUG=0`; si falta, `web` no arranca (`ImproperlyConfigured`) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Dominios desde los que se acepta la API. Dejar siempre `127.0.0.1`: lo usa el healthcheck (`GET http://127.0.0.1:8000/`, la home, que no depende de los permisos de la API) |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Orígenes del frontend que pueden llamar a la API |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | vacío | Orígenes `https://` confiables (login del admin en un dominio público) |
| `DJANGO_SECURE_COOKIES` | `= not DEBUG` | Cookies de sesión/CSRF solo por HTTPS |

Fijas en `compose.yaml` (no tocar): `DB_HOST=db`, `DB_PORT=5432`, `DJANGO_MEDIA_ROOT=/app/media`.
Sin `DB_HOST` (por ejemplo con `runserver` local) Django usa SQLite.

Producción local de prueba:

```bash
DJANGO_DEBUG=0 DJANGO_SECRET_KEY=$(openssl rand -hex 32) docker compose up -d
```

## Por qué la base no publica puerto

`db` no tiene `ports:`. Solo es accesible dentro de la red interna que crea Compose, donde `web` la encuentra por el **nombre del servicio** (`db:5432`). Dentro de un contenedor, `localhost` es el propio contenedor, no la máquina ni la base. No publicar el puerto evita exponer PostgreSQL a la red. `web` se publica en `127.0.0.1:8000`, así que solo se accede desde la propia máquina.

## Limitación: archivos media

Las imágenes de productos (`ImageField`) se guardan en el volumen `media_data` (`/app/media`) y las sirve Django con `django.views.static.serve` (ruta `media/` en `config/urls.py`), también con `DEBUG=0`. Funciona para el alcance del proyecto, pero no es eficiente ni pensado para producción. En un despliegue real conviene servir `/media/` desde un proxy inverso (nginx) o un almacenamiento de objetos (S3).
