from conexion import get_connection_pool
from src.services.inventario_service import ProveedorService


def proveedores(pool):
    return ProveedorService().listar()


def añadir_proveedor(pool, nombre, direccion, email):
    return ProveedorService().crear_proveedor(nombre=nombre, direccion=direccion, email=email)


def actualizar_proveedor(pool, id_proveedor, nombre, direccion, email):
    return ProveedorService().actualizar_proveedor(
        id_proveedor=id_proveedor, nombre=nombre, direccion=direccion, email=email
    )


def eliminar_proveedor(pool, id_proveedor):
    return ProveedorService().eliminar_proveedor(id_proveedor)
