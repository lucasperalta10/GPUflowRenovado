from typing import Optional
import pandas as pd
from sqlalchemy import select
from src.core.orm import ProveedorORM
from src.models.proveedor import Proveedor
from src.repositories.base_repository import BaseRepository


class ProveedorRepository(BaseRepository):
    """
    Repositorio encargado de las operaciones CRUD sobre ProveedorORM.
    """

    def obtener_todos_df(self) -> pd.DataFrame:
        stmt = select(ProveedorORM.id_proveedor, ProveedorORM.Nombre).order_by(ProveedorORM.Nombre)
        rows = self.session.execute(stmt).mappings().all()
        return pd.DataFrame(rows)

    def obtener_todos_completos_df(self) -> pd.DataFrame:
        stmt = select(
            ProveedorORM.id_proveedor,
            ProveedorORM.Nombre,
            ProveedorORM.Direccion,
            ProveedorORM.Correo_Electronico,
        ).order_by(ProveedorORM.Nombre)
        rows = self.session.execute(stmt).mappings().all()
        return pd.DataFrame(rows)

    def obtener_por_id(self, id_proveedor: int) -> Optional[Proveedor]:
        row = self.session.get(ProveedorORM, id_proveedor)
        if row is None:
            return None
        return Proveedor(
            id_proveedor=row.id_proveedor,
            nombre=row.Nombre,
            direccion=row.Direccion or "",
            email=row.Correo_Electronico or "",
        )

    def crear(self, proveedor: Proveedor) -> Proveedor:
        row = ProveedorORM(
            Nombre=proveedor.nombre,
            Direccion=proveedor.direccion,
            Correo_Electronico=proveedor.email,
        )
        self.session.add(row)
        self.session.flush()
        proveedor.id_proveedor = row.id_proveedor
        return proveedor

    def actualizar(self, proveedor: Proveedor) -> Optional[Proveedor]:
        row = self.session.get(ProveedorORM, proveedor.id_proveedor)
        if row is None:
            return None
        row.Nombre = proveedor.nombre
        row.Direccion = proveedor.direccion
        row.Correo_Electronico = proveedor.email
        self.session.flush()
        return proveedor

    def eliminar(self, id_proveedor: int) -> bool:
        row = self.session.get(ProveedorORM, id_proveedor)
        if row is None:
            return False
        self.session.delete(row)
        self.session.flush()
        return True
