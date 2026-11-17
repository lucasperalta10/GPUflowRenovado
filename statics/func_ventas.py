from conexion import get_connection_pool
from src.services.inventario_service import VentaService


def proceso_transaccion(pool, id_empleado, cart):
    return VentaService().procesar_venta(id_empleado=id_empleado, cart=cart)


def resumen_ventas(pool):
    return VentaService().resumen_ventas()


def detalles_venta(pool, id_compra):
    return VentaService().detalles_venta(id_compra)
