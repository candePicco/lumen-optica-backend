"""
Tests de infraestructura: configuracion por entorno, CORS y ALLOWED_HOSTS.

Regla: nunca se usa override_settings sobre el setting que se esta
probando; cada categoria verifica el valor real de config/settings.py.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase, override_settings

from config import env


def run_settings_subprocess(code, extra_env):
    """Importa config.settings en un proceso limpio, sin heredar os.environ.

    Dentro del contenedor hay DB_HOST, POSTGRES_* y DJANGO_* definidos;
    heredarlos haria que el resultado dependa del entorno.
    """
    child_env = {
        key: os.environ[key]
        for key in ("PATH", "HOME", "LANG")
        if key in os.environ
    }
    child_env.update(extra_env)
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=settings.BASE_DIR,
        env=child_env,
        capture_output=True,
        text=True,
        timeout=60,
    )


class EnvParseTests(SimpleTestCase):
    def test_env_bool_true_values(self):
        for value in ["1", "true", "TRUE", "Yes", "on", " On "]:
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {"X_FLAG": value}, clear=True):
                    self.assertIs(env.env_bool("X_FLAG", False), True)

    def test_env_bool_false_values(self):
        for value in ["0", "false", "FALSE", "No", "off", " OFF "]:
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {"X_FLAG": value}, clear=True):
                    self.assertIs(env.env_bool("X_FLAG", True), False)

    def test_env_bool_invalid_raises(self):
        for value in ["", "si", "2", "verdadero"]:
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {"X_FLAG": value}, clear=True):
                    with self.assertRaises(ImproperlyConfigured):
                        env.env_bool("X_FLAG", True)

    def test_env_bool_default_when_unset(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIs(env.env_bool("X_FLAG", True), True)
            self.assertIs(env.env_bool("X_FLAG", False), False)

    def test_env_list_strips_and_drops_empties(self):
        with mock.patch.dict(
            os.environ, {"X_LIST": " a.com , ,b.com,, "}, clear=True
        ):
            self.assertEqual(env.env_list("X_LIST", ["z"]), ["a.com", "b.com"])

    def test_env_list_default_when_unset(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(env.env_list("X_LIST", ["z"]), ["z"])

    def test_env_str_default_when_unset(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(env.env_str("X_STR", "def"), "def")
        with mock.patch.dict(os.environ, {"X_STR": "val"}, clear=True):
            self.assertEqual(env.env_str("X_STR", "def"), "val")


class DbSelectTests(SimpleTestCase):
    base_dir = Path("/proyecto")

    def test_without_db_host_uses_sqlite(self):
        db = env.build_databases({}, self.base_dir)["default"]
        self.assertEqual(db["ENGINE"], "django.db.backends.sqlite3")
        self.assertEqual(db["NAME"], self.base_dir / "db.sqlite3")

    def test_empty_db_host_uses_sqlite(self):
        db = env.build_databases({"DB_HOST": ""}, self.base_dir)["default"]
        self.assertEqual(db["ENGINE"], "django.db.backends.sqlite3")

    def test_db_host_with_password_uses_postgresql(self):
        db = env.build_databases(
            {
                "DB_HOST": "db",
                "POSTGRES_DB": "lumen_optica",
                "POSTGRES_USER": "lumen",
                "POSTGRES_PASSWORD": "secreto",
            },
            self.base_dir,
        )["default"]
        self.assertEqual(db["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(db["HOST"], "db")
        self.assertEqual(db["PORT"], "5432")
        self.assertEqual(db["NAME"], "lumen_optica")
        self.assertEqual(db["USER"], "lumen")
        self.assertEqual(db["PASSWORD"], "secreto")
        self.assertIs(db["CONN_HEALTH_CHECKS"], True)

    def test_db_port_from_environ(self):
        db = env.build_databases(
            {"DB_HOST": "db", "DB_PORT": "6543", "POSTGRES_PASSWORD": "x"},
            self.base_dir,
        )["default"]
        self.assertEqual(db["PORT"], "6543")

    def test_db_host_without_password_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            env.build_databases({"DB_HOST": "db"}, self.base_dir)


class SecretFailFastTests(SimpleTestCase):
    def test_debug_off_without_key_fails(self):
        result = run_settings_subprocess(
            "import config.settings", {"DJANGO_DEBUG": "0"}
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ImproperlyConfigured", result.stderr)

    def test_debug_off_with_key_succeeds(self):
        result = run_settings_subprocess(
            "import config.settings",
            {"DJANGO_DEBUG": "0", "DJANGO_SECRET_KEY": "x"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)


class CorsAllowTests(TestCase):
    def test_preflight_from_allowed_origin(self):
        response = self.client.options(
            "/api/productos/",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "http://localhost:3000",
        )


class CorsDenyTests(TestCase):
    def test_preflight_from_unknown_origin(self):
        response = self.client.options(
            "/api/productos/",
            HTTP_ORIGIN="https://evil.example",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)


@override_settings(DEBUG=False)
class HostsTests(TestCase):
    # ALLOWED_HOSTS real + "testserver" (lo agrega el test runner).
    def test_unknown_host_rejected(self):
        response = self.client.get("/api/", HTTP_HOST="evil.example")
        self.assertEqual(response.status_code, 400)

    def test_test_host_accepted(self):
        response = self.client.get("/api/", HTTP_HOST="testserver")
        self.assertNotEqual(response.status_code, 400)

    def test_allowed_hosts_parsed_from_env(self):
        result = run_settings_subprocess(
            "import json, config.settings as s; print(json.dumps(s.ALLOWED_HOSTS))",
            {
                "DJANGO_DEBUG": "0",
                "DJANGO_SECRET_KEY": "x",
                "DJANGO_ALLOWED_HOSTS": " api.example.com , ,localhost",
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout), ["api.example.com", "localhost"]
        )
