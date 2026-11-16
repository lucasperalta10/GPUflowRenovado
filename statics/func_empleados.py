from conexion import get_connection_pool
from models.empleado import Empleado
from repositories.empleado_repository import EmpleadoRepository


def empleados(pool):
    return EmpleadoRepository(pool).obtener_todos_df()


def añadir_empleado(pool, nombre, apellido, cargo):
    nuevo = Empleado(nombre=nombre, apellido=apellido, cargo=cargo)
    return EmpleadoRepository(pool).crear(nuevo)


def actualizar_empleado(pool, id_empleado, nombre, apellido, cargo):
    editado = Empleado(id_empleado=id_empleado, nombre=nombre, apellido=apellido, cargo=cargo)
    return EmpleadoRepository(pool).actualizar(editado)
