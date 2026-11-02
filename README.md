# Lumen Óptica — API backend

Backend REST para administrar el catálogo de una óptica y sus clientes, pedidos y pagos. Está construido con Django y Django REST Framework; usa SQLite por defecto.

## Requisitos

- Python 3.12 o superior
- [uv](https://docs.astral.sh/uv/) para instalar las dependencias del proyecto

## Instalación y ejecución local

Desde la carpeta del proyecto:

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

El servidor queda disponible en `http://127.0.0.1:8000/`. La base local `db.sqlite3` se crea en la carpeta del proyecto y está excluida de Git.

## Panel de administración

Ingresa a `http://127.0.0.1:8000/admin/` con el usuario creado mediante `createsuperuser`. El panel permite administrar categorías, marcas, proveedores, productos e imágenes, clientes, direcciones, pedidos, detalles y pagos. Las imágenes se editan junto al producto; los detalles y pagos se editan desde el pedido.

El panel requiere una cuenta con permisos de staff. No se debe habilitar el acceso anónimo.

## Documentación interactiva

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- Redoc: `http://127.0.0.1:8000/api/redoc/`
- Esquema OpenAPI: `http://127.0.0.1:8000/api/schema/`

Los endpoints de escritura requieren autenticación. Para obtener un par de tokens JWT, envía usuario y contraseña a `POST /api/token/`; usa el access token con el encabezado `Authorization: Bearer <access>`. `POST /api/token/refresh/` permite renovar el access token.

## Endpoints

Todos los recursos están bajo `/api/`. Los ViewSets exponen las operaciones REST indicadas; las escrituras necesitan autenticación y las lecturas son públicas.

| Recurso | Ruta | Acciones especiales |
| --- | --- | --- |
| Categorías | `/api/categorias/` | — |
| Marcas | `/api/marcas/` | — |
| Proveedores | `/api/proveedores/` | — |
| Productos | `/api/productos/` | `GET /api/productos/destacados/` |
| Imágenes de producto | `/api/imagenes-producto/` | — |
| Clientes | `/api/clientes/` | — |
| Direcciones | `/api/direcciones/` | — |
| Pedidos | `/api/pedidos/` | `POST /api/pedidos/{id}/cancelar/` |
| Detalles de pedido | `/api/detalles-pedido/` | — |
| Pagos | `/api/pagos/` | — |

Las listas se paginan con 10 elementos por página. Productos permiten filtrar por `categoria`, `marca`, `destacado` y `activo`, buscar por `nombre` o `descripcion`, y ordenar por `nombre`, `precio` o `stock`.

Ejemplo para listar categorías:

```bash
curl http://127.0.0.1:8000/api/categorias/
```

## Pruebas

Ejecuta la suite de pruebas de Django:

```bash
uv run python manage.py test
```

Las pruebas cubren el registro y acceso del panel de administración, lectura pública y escritura autenticada de la API, y disponibilidad de Swagger, Redoc y el esquema OpenAPI.

## Estructura

```text
config/       Configuración Django y rutas del proyecto
optica/       Modelos, administración, serializadores, endpoints y pruebas
manage.py     Comandos de administración de Django
```
