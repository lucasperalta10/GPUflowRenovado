from typing import Optional
import pandas as pd
from sqlalchemy import select
from src.core.orm import MarcaORM, ProductoORM, ProveedorORM
from src.models.producto import Producto
from src.repositories.base_repository import BaseRepository


class ProductoRepository(BaseRepository):
    """
    Repositorio encargado de las operaciones CRUD y consultas sobre ProductoORM y MarcaORM.
    """

    def _obtener_o_crear_marca(self, nombre_marca: Optional[str]) -> Optional[int]:
        if not nombre_marca:
            return None
        nombre = nombre_marca.strip()
        if not nombre:
            return None

        stmt = select(MarcaORM).where(MarcaORM.nombre_marca == nombre)
        marca_row = self.session.scalar(stmt)
        if marca_row:
            return marca_row.id_marca

        nueva_marca = MarcaORM(nombre_marca=nombre)
        self.session.add(nueva_marca)
        self.session.flush()
        return nueva_marca.id_marca

    def obtener_todos_df(self) -> pd.DataFrame:
        stmt = (
            select(
                ProductoORM.id_producto.label("ID"),
                ProductoORM.Nombre,
                MarcaORM.nombre_marca.label("Marca"),
                ProductoORM.Modelo,
                ProductoORM.Memoria_VRAM.label("VRAM"),
                ProductoORM.Precio,
                ProductoORM.Stock,
                ProveedorORM.Nombre.label("Proveedor"),
            )
            .outerjoin(ProveedorORM, ProductoORM.id_proveedor == ProveedorORM.id_proveedor)
            .outerjoin(MarcaORM, ProductoORM.id_marca == MarcaORM.id_marca)
            .order_by(MarcaORM.nombre_marca, ProductoORM.Modelo)
        )
        rows = self.session.execute(stmt).mappings().all()
        df = pd.DataFrame(rows)
        if not df.empty and "Precio" in df.columns:
            df["Precio"] = df["Precio"].astype(float)
        return df

    def obtener_disponibles_df(self) -> pd.DataFrame:
        stmt = (
            select(
                ProductoORM.id_producto,
                ProductoORM.Nombre,
                MarcaORM.nombre_marca.label("Marca"),
                ProductoORM.Modelo,
                ProductoORM.Precio,
                ProductoORM.Stock,
            )
            .outerjoin(MarcaORM, ProductoORM.id_marca == MarcaORM.id_marca)
            .where(ProductoORM.Stock > 0)
            .order_by(MarcaORM.nombre_marca, ProductoORM.Modelo)
        )
        rows = self.session.execute(stmt).mappings().all()
        df = pd.DataFrame(rows)
        if not df.empty and "Precio" in df.columns:
            df["Precio"] = df["Precio"].astype(float)
        return df

    def obtener_stock_bajo_df(self, umbral: int = 10) -> pd.DataFrame:
        stmt = (
            select(
                ProductoORM.Nombre,
                MarcaORM.nombre_marca.label("Marca"),
                ProductoORM.Modelo,
                ProductoORM.Stock,
            )
            .outerjoin(MarcaORM, ProductoORM.id_marca == MarcaORM.id_marca)
            .where(ProductoORM.Stock <= umbral, ProductoORM.Stock > 0)
            .order_by(ProductoORM.Stock.asc())
        )
        rows = self.session.execute(stmt).mappings().all()
        return pd.DataFrame(rows)

    def obtener_por_id(self, id_producto: int) -> Optional[ProductoORM]:
        return self.session.get(ProductoORM, id_producto)

    def crear(self, producto: Producto) -> Producto:
        id_marca = self._obtener_o_crear_marca(producto.marca)
        row = ProductoORM(
            Nombre=producto.nombre,
            Modelo=producto.modelo,
            Memoria_VRAM=producto.vram,
            Precio=producto.precio,
            Stock=producto.stock,
            id_marca=id_marca,
            id_proveedor=producto.id_proveedor,
        )
        self.session.add(row)
        self.session.flush()
        producto.id_producto = row.id_producto
        return producto

    def actualizar(self, producto: Producto) -> Optional[Producto]:
        row = self.session.get(ProductoORM, producto.id_producto)
        if row is None:
            return None
        row.Nombre = producto.nombre
        row.Modelo = producto.modelo
        row.Memoria_VRAM = producto.vram
        row.Precio = producto.precio
        row.Stock = producto.stock
        row.id_marca = self._obtener_o_crear_marca(producto.marca)
        row.id_proveedor = producto.id_proveedor
        self.session.flush()
        return producto

    def eliminar(self, id_producto: int) -> bool:
        row = self.session.get(ProductoORM, id_producto)
        if row is None:
            return False
        self.session.delete(row)
        self.session.flush()
        return True
