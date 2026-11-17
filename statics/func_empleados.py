from conexion import get_connection_pool
from src.services.inventario_service import EmpleadoService


def empleados(pool):
    return EmpleadoService().listar()


def añadir_empleado(pool, nombre, apellido, cargo):
    return EmpleadoService().crear_empleado(nombre=nombre, apellido=apellido, cargo=cargo)


def actualizar_empleado(pool, id_empleado, nombre, apellido, cargo):
    return EmpleadoService().actualizar_empleado(
        id_empleado=id_empleado, nombre=nombre, apellido=apellido, cargo=cargo
    )
