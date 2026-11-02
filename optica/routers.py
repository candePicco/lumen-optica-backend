from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet,
    ClienteViewSet,
    DetallePedidoViewSet,
    DireccionViewSet,
    ImagenProductoViewSet,
    MarcaViewSet,
    PagoViewSet,
    PedidoViewSet,
    ProductoViewSet,
    ProveedorViewSet,
)


router = DefaultRouter()

router.register(
    "categorias",
    CategoriaViewSet,
    basename="categoria",
)

router.register(
    "marcas",
    MarcaViewSet,
    basename="marca",
)

router.register(
    "proveedores",
    ProveedorViewSet,
    basename="proveedor",
)

router.register(
    "productos",
    ProductoViewSet,
    basename="producto",
)

router.register(
    "imagenes-producto",
    ImagenProductoViewSet,
    basename="imagen-producto",
)

router.register(
    "clientes",
    ClienteViewSet,
    basename="cliente",
)

router.register(
    "direcciones",
    DireccionViewSet,
    basename="direccion",
)

router.register(
    "pedidos",
    PedidoViewSet,
    basename="pedido",
)

router.register(
    "detalles-pedido",
    DetallePedidoViewSet,
    basename="detalle-pedido",
)

router.register(
    "pagos",
    PagoViewSet,
    basename="pago",
)


urlpatterns = router.urls