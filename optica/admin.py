from django.contrib import admin

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


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre"]
    search_fields = ["nombre"]


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre"]
    search_fields = ["nombre"]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "telefono", "email"]
    search_fields = ["nombre", "email"]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nombre",
        "precio",
        "stock",
        "categoria",
        "marca",
        "destacado",
        "activo",
    ]
    search_fields = ["nombre"]
    list_filter = [
        "categoria",
        "marca",
        "destacado",
        "activo",
    ]
    ordering = ["nombre"]


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "producto",
        "principal",
    ]
    list_filter = ["principal"]


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nombre",
        "apellido",
        "dni",
        "telefono",
        "usuario",
    ]
    search_fields = [
        "nombre",
        "apellido",
        "dni",
    ]
    ordering = ["apellido", "nombre"]


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cliente",
        "calle",
        "numero",
        "ciudad",
        "provincia",
    ]
    search_fields = [
        "cliente__nombre",
        "cliente__apellido",
        "ciudad",
    ]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cliente",
        "fecha",
        "estado",
        "total",
    ]
    list_filter = ["estado", "fecha"]
    search_fields = [
        "cliente__nombre",
        "cliente__apellido",
    ]
    ordering = ["-fecha"]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "pedido",
        "producto",
        "cantidad",
        "precio_unitario",
    ]


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "pedido",
        "monto",
        "metodo",
        "estado",
        "fecha",
    ]
    list_filter = [
        "metodo",
        "estado",
    ]
    ordering = ["-fecha"]