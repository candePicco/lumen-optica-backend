from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
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
from .serializers import (
    CategoriaSerializer,
    ClienteSerializer,
    DetallePedidoSerializer,
    DetallePedidoWriteSerializer,
    DireccionSerializer,
    ImagenProductoSerializer,
    MarcaSerializer,
    PagoSerializer,
    PedidoPublicSerializer,
    PedidoSerializer,
    ProductoPublicSerializer,
    ProductoSerializer,
    ProveedorSerializer,
)


def home(request):
    return render(request, "optica/home.html")

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().select_related(
        "categoria",
        "marca",
        "proveedor",
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    filterset_fields = [
        "categoria",
        "marca",
        "destacado",
        "activo",
    ]

    search_fields = [
    "nombre",
    "descripcion",
    "marca__nombre",
    ]

    ordering_fields = [
        "nombre",
        "precio",
        "stock",
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductoPublicSerializer
        return ProductoSerializer

    @action(detail=False, methods=["get"])
    def destacados(self, request):
        productos = self.get_queryset().filter(destacado=True)

        serializer = ProductoPublicSerializer(
            productos,
            many=True,
        )

        return Response(serializer.data)
class ImagenProductoViewSet(viewsets.ModelViewSet):
    queryset = ImagenProducto.objects.all().select_related("producto")
    serializer_class = ImagenProductoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().select_related("usuario")
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DireccionViewSet(viewsets.ModelViewSet):
    queryset = Direccion.objects.all().select_related("cliente")
    serializer_class = DireccionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().select_related(
        "cliente",
        "direccion",
    ).prefetch_related(
        "detalles",
        "detalles__producto",
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return PedidoPublicSerializer
        return PedidoSerializer

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        pedido = self.get_object()
        pedido.estado = Pedido.Estado.CANCELADO
        pedido.save()

        serializer = self.get_serializer(pedido)
        return Response(serializer.data)

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all().select_related(
        "pedido",
        "producto",
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return DetallePedidoSerializer
        return DetallePedidoWriteSerializer


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all().select_related("pedido")
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]