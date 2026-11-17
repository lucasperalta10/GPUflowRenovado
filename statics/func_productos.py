from conexion import get_connection_pool
from src.services.inventario_service import ProductoService


def obtener_productos(pool):
    return ProductoService().listar()


def productos_y_precios_disponibles(pool):
    return ProductoService().listar_disponibles()


def obtener_stock_bajo(pool, umbral=10):
    return ProductoService().listar_stock_bajo(umbral=umbral)


def añadir_producto(pool, nombre, marca, modelo, vram, precio, stock, id_proveedor):
    ok, _ = ProductoService().crear_producto(
        nombre=nombre, marca=marca, modelo=modelo, vram=vram,
        precio=precio, stock=stock, id_proveedor=id_proveedor
    )
    return ok


def actualizar_producto(pool, id_producto, nombre, marca, modelo, vram, precio, stock, id_proveedor):
    ok, _ = ProductoService().actualizar_producto(
        id_producto=id_producto, nombre=nombre, marca=marca, modelo=modelo,
        vram=vram, precio=precio, stock=stock, id_proveedor=id_proveedor
    )
    return ok


def eliminar_producto(pool, id_producto):
    return ProductoService().eliminar_producto(id_producto)
