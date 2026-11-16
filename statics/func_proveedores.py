from conexion import get_connection_pool
from models.proveedor import Proveedor
from repositories.proveedor_repository import ProveedorRepository


def proveedores(pool):
    return ProveedorRepository(pool).obtener_todos_df()


def añadir_proveedor(pool, nombre, direccion, email):
    nuevo = Proveedor(nombre=nombre, direccion=direccion, email=email)
    return ProveedorRepository(pool).crear(nuevo)


def actualizar_proveedor(pool, id_proveedor, nombre, direccion, email):
    editado = Proveedor(id_proveedor=id_proveedor, nombre=nombre, direccion=direccion, email=email)
    return ProveedorRepository(pool).actualizar(editado)


def eliminar_proveedor(pool, id_proveedor):
    return ProveedorRepository(pool).eliminar(id_proveedor)
