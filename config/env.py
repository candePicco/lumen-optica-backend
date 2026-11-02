"""
Lectura de configuracion desde variables de entorno (solo stdlib).

Se mantiene separado de settings.py para poder testear el parseo sin
importar la configuracion de Django.
"""

import os
from collections.abc import Mapping
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


def env_str(name, default=""):
    return os.environ.get(name, default)


def env_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ImproperlyConfigured(
        f"{name}={value!r} no es un booleano valido "
        f"(usar uno de: {', '.join(sorted(TRUE_VALUES | FALSE_VALUES))})."
    )


def env_list(name, default):
    value = os.environ.get(name)
    if value is None:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def build_databases(environ: Mapping[str, str], base_dir) -> dict:
    """PostgreSQL si DB_HOST esta definido (Docker Compose); si no, SQLite local."""
    host = environ.get("DB_HOST", "").strip()
    if host:
        password = environ.get("POSTGRES_PASSWORD", "")
        if not password:
            raise ImproperlyConfigured(
                "DB_HOST esta definido pero falta POSTGRES_PASSWORD."
            )
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "HOST": host,
                "PORT": environ.get("DB_PORT", "") or "5432",
                "NAME": environ.get("POSTGRES_DB", "lumen_optica"),
                "USER": environ.get("POSTGRES_USER", "lumen"),
                "PASSWORD": password,
                "CONN_HEALTH_CHECKS": True,
            }
        }
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(base_dir) / "db.sqlite3",
        }
    }
