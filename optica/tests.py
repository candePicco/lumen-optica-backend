from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import (
    Categoria,
    Cliente,
    DetallePedido,
    Direccion,
    ImagenProducto,
    Marca,
    Pago,
    Pedido,
    Producto,
    Proveedor,
)


class AdminTests(TestCase):
    def test_business_models_are_registered(self):
        for model in (
            Categoria,
            Marca,
            Proveedor,
            Producto,
            ImagenProducto,
            Cliente,
            Direccion,
            Pedido,
            DetallePedido,
            Pago,
        ):
            with self.subTest(model=model.__name__):
                self.assertIn(model, admin.site._registry)

    def test_admin_requires_staff_login(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)

    def test_staff_user_can_open_admin(self):
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password-123",
        )
        self.client.login(username="admin", password="test-password-123")

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)


class ApiEndpointTests(TestCase):
    def setUp(self):
        self.api = APIClient()

    def test_category_list_is_public_and_paginated(self):
        Categoria.objects.create(nombre="Armazones")

        response = self.api.get("/api/categorias/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nombre"], "Armazones")

    def test_anonymous_user_cannot_create_category(self):
        response = self.api.post(
            "/api/categorias/",
            {"nombre": "Lentes de sol", "descripcion": "Protección UV"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Categoria.objects.count(), 0)

    def test_authenticated_user_can_create_and_read_category(self):
        user = User.objects.create_user(username="api-user", password="test-password-123")
        self.api.force_authenticate(user=user)

        created = self.api.post(
            "/api/categorias/",
            {"nombre": "Lentes de sol", "descripcion": "Protección UV"},
            format="json",
        )

        self.assertEqual(created.status_code, 201)
        detail = self.api.get(f"/api/categorias/{created.data['id']}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["nombre"], "Lentes de sol")

    def test_documentation_pages_are_available(self):
        for url in ("/api/schema/", "/api/docs/", "/api/redoc/"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_home_links_to_api_documentation_and_admin(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        for link in ("/api/docs/", "/api/redoc/", "/admin/"):
            with self.subTest(link=link):
                self.assertContains(response, link)
