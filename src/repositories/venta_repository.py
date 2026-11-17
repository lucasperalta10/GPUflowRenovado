from datetime import datetime
import pandas as pd
from sqlalchemy import func, select, update
from src.core.orm import CompraORM, DetalleCompraORM, EmpleadoORM, MarcaORM, ProductoORM
from src.models.venta import Venta
from src.repositories.base_repository import BaseRepository


class VentaRepository(BaseRepository):
    """
    Repositorio encargado de las transacciones de venta (CompraORM y DetalleCompraORM).
    """

    def registrar_venta(self, venta: Venta) -> int:
        fecha = datetime.strptime(venta.fecha_hora, "%Y-%m-%d %H:%M:%S")
        compra_row = CompraORM(
            Fecha_hora=fecha,
            id_empleado=venta.id_empleado,
        )
        self.session.add(compra_row)
        self.session.flush()

        new_compra_id = compra_row.id_compra
        venta.id_compra = new_compra_id

        for item in venta.items:
            stmt_stock = (
                update(ProductoORM)
                .where(
                    ProductoORM.id_producto == item.id_producto,
                    ProductoORM.Stock >= item.cantidad,
                )
                .values(Stock=ProductoORM.Stock - item.cantidad)
            )
            result = self.session.execute(stmt_stock)
            if result.rowcount == 0:
                raise ValueError(f"Stock insuficiente para {item.nombre}. Venta cancelada.")

            detalle_row = DetalleCompraORM(
                Cantidad=item.cantidad,
                Subtotal=item.subtotal,
                id_producto=item.id_producto,
                id_compra=new_compra_id,
            )
            self.session.add(detalle_row)

        self.session.flush()
        return new_compra_id

    def obtener_resumen_df(self) -> pd.DataFrame:
        stmt = (
            select(
                CompraORM.id_compra,
                CompraORM.Fecha_hora.label("Fecha"),
                func.coalesce(func.sum(DetalleCompraORM.Subtotal), 0).label("Monto_total"),
                func.concat(EmpleadoORM.Apellido, ", ", EmpleadoORM.Nombre).label("Empleado"),
            )
            .outerjoin(DetalleCompraORM, DetalleCompraORM.id_compra == CompraORM.id_compra)
            .join(EmpleadoORM, CompraORM.id_empleado == EmpleadoORM.id_empleado)
            .group_by(
                CompraORM.id_compra,
                CompraORM.Fecha_hora,
                EmpleadoORM.Apellido,
                EmpleadoORM.Nombre,
            )
            .order_by(CompraORM.Fecha_hora.desc(), CompraORM.id_compra.desc())
        )
        rows = self.session.execute(stmt).mappings().all()
        df = pd.DataFrame(rows)
        if not df.empty and "Monto_total" in df.columns:
            df["Monto_total"] = df["Monto_total"].astype(float)
        return df

    def obtener_detalles_df(self, id_compra: int) -> pd.DataFrame:
        stmt = (
            select(
                DetalleCompraORM.Cantidad,
                ProductoORM.Nombre.label("Producto"),
                MarcaORM.nombre_marca.label("Marca"),
                ProductoORM.Modelo,
                DetalleCompraORM.Subtotal,
            )
            .join(ProductoORM, DetalleCompraORM.id_producto == ProductoORM.id_producto)
            .outerjoin(MarcaORM, ProductoORM.id_marca == MarcaORM.id_marca)
            .where(DetalleCompraORM.id_compra == id_compra)
        )
        rows = self.session.execute(stmt).mappings().all()
        df = pd.DataFrame(rows)
        if not df.empty and "Subtotal" in df.columns:
            df["Subtotal"] = df["Subtotal"].astype(float)
        return df
