from rest_framework import serializers

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


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"
        read_only_fields = ["id"]


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = "__all__"
        read_only_fields = ["id"]


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = "__all__"
        read_only_fields = ["id"]


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = "__all__"
        read_only_fields = ["id"]


class ProductoPublicSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "destacado",
            "activo",
            "categoria",
            "marca",
        ]
        read_only_fields = ["id"]


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = "__all__"
        read_only_fields = ["id"]


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"
        read_only_fields = ["id"]


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = "__all__"
        read_only_fields = ["id"]


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto = ProductoPublicSerializer(read_only=True)

    class Meta:
        model = DetallePedido
        fields = [
            "id",
            "producto",
            "cantidad",
            "precio_unitario",
        ]
        read_only_fields = ["id"]


class PedidoPublicSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    direccion = DireccionSerializer(read_only=True)
    detalles = DetallePedidoSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Pedido
        fields = [
            "id",
            "cliente",
            "direccion",
            "fecha",
            "estado",
            "total",
            "detalles",
        ]
        read_only_fields = [
            "id",
            "fecha",
        ]


class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = "__all__"
        read_only_fields = [
            "id",
            "fecha",
        ]


class DetallePedidoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = "__all__"
        read_only_fields = ["id"]


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = "__all__"
        read_only_fields = [
            "id",
            "fecha",
        ]