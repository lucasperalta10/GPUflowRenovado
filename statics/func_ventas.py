from conexion import get_connection_pool
from models.venta import ItemVenta, Venta
from repositories.venta_repository import VentaRepository


def proceso_transaccion(pool, id_empleado, cart):
    items = [ItemVenta.from_dict(item) for item in cart]
    venta = Venta(id_empleado=id_empleado, items=items)
    return VentaRepository(pool).registrar_venta(venta)


def resumen_ventas(pool):
    return VentaRepository(pool).obtener_resumen_df()


def detalles_venta(pool, id_compra):
    return VentaRepository(pool).obtener_detalles_df(id_compra)
