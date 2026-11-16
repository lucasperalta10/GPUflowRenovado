from conexion import get_connection_pool
from models.producto import Producto
from repositories.producto_repository import ProductoRepository


def obtener_productos(pool):
    return ProductoRepository(pool).obtener_todos_df()


def productos_y_precios_disponibles(pool):
    return ProductoRepository(pool).obtener_disponibles_df()


def obtener_stock_bajo(pool, umbral=10):
    return ProductoRepository(pool).obtener_stock_bajo_df(umbral=umbral)


def añadir_producto(pool, nombre, marca, modelo, vram, precio, stock, id_proveedor):
    nuevo = Producto(
        nombre=nombre, marca=marca, modelo=modelo, vram=vram,
        precio=precio, stock=stock, id_proveedor=id_proveedor
    )
    return ProductoRepository(pool).crear(nuevo)


def actualizar_producto(pool, id_producto, nombre, marca, modelo, vram, precio, stock, id_proveedor):
    editado = Producto(
        id_producto=id_producto, nombre=nombre, marca=marca, modelo=modelo,
        vram=vram, precio=precio, stock=stock, id_proveedor=id_proveedor
    )
    return ProductoRepository(pool).actualizar(editado)


def eliminar_producto(pool, id_producto):
    return ProductoRepository(pool).eliminar(id_producto)
