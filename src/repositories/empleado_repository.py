from typing import Optional
import pandas as pd
from sqlalchemy import select
from src.core.orm import CargoORM, EmpleadoORM
from src.models.empleado import Empleado
from src.repositories.base_repository import BaseRepository


class EmpleadoRepository(BaseRepository):
    """
    Repositorio encargado de las operaciones CRUD sobre EmpleadoORM y CargoORM.
    """

    def _obtener_o_crear_cargo(self, nombre_cargo: Optional[str]) -> Optional[int]:
        if not nombre_cargo:
            return None
        nombre = nombre_cargo.strip()
        if not nombre or nombre == "(Ninguno)":
            return None

        stmt = select(CargoORM).where(CargoORM.nombre_cargo == nombre)
        cargo_row = self.session.scalar(stmt)
        if cargo_row:
            return cargo_row.id_cargo

        nuevo_cargo = CargoORM(nombre_cargo=nombre)
        self.session.add(nuevo_cargo)
        self.session.flush()
        return nuevo_cargo.id_cargo

    def obtener_todos_df(self) -> pd.DataFrame:
        stmt = (
            select(
                EmpleadoORM.id_empleado.label("ID"),
                EmpleadoORM.Nombre,
                EmpleadoORM.Apellido,
                CargoORM.nombre_cargo.label("Cargo"),
            )
            .outerjoin(CargoORM, EmpleadoORM.id_cargo == CargoORM.id_cargo)
            .order_by(EmpleadoORM.Apellido)
        )
        rows = self.session.execute(stmt).mappings().all()
        return pd.DataFrame(rows)

    def crear(self, empleado: Empleado) -> Empleado:
        id_cargo = self._obtener_o_crear_cargo(empleado.cargo)
        row = EmpleadoORM(
            Nombre=empleado.nombre,
            Apellido=empleado.apellido,
            id_cargo=id_cargo,
            password=empleado.password,
        )
        self.session.add(row)
        self.session.flush()
        empleado.id_empleado = row.id_empleado
        return empleado

    def actualizar(self, empleado: Empleado) -> Optional[Empleado]:
        row = self.session.get(EmpleadoORM, empleado.id_empleado)
        if row is None:
            return None
        row.Nombre = empleado.nombre
        row.Apellido = empleado.apellido
        row.id_cargo = self._obtener_o_crear_cargo(empleado.cargo)
        self.session.flush()
        return empleado
