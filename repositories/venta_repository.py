import streamlit as st
import pandas as pd
from models.venta import Venta
from repositories.base_repository import BaseRepository


class VentaRepository(BaseRepository):
    """
    Repositorio encargado de las transacciones de venta (Compra y Detalle_Compra) y reportes.
    """

    def registrar_venta(self, venta: Venta) -> tuple[bool, str]:
        if not self._tiene_conexion():
            return False, "Error de conexión"
        if venta.esta_vacia():
            return False, "El carrito está vacío"

        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            conn.autocommit = False

            query_compra = """
                INSERT INTO Compra (Fecha_hora, id_empleado)
                VALUES (%s, %s)
            """
            cursor.execute(query_compra, (venta.fecha_hora, venta.id_empleado))

            new_compra_id = cursor.lastrowid
            if not new_compra_id:
                raise RuntimeError("No se pudo obtener el ID de la nueva compra.")

            venta.id_compra = new_compra_id

            for item in venta.items:
                query_stock = """
                    UPDATE Producto
                    SET Stock = Stock - %s
                    WHERE id_producto = %s AND Stock >= %s
                """
                cursor.execute(query_stock, (item.cantidad, item.id_producto, item.cantidad))

                if cursor.rowcount == 0:
                    raise ValueError(f"Stock insuficiente para {item.nombre}. Venta cancelada.")

                query_detalle = """
                    INSERT INTO Detalle_Compra (Cantidad, Subtotal, id_producto, id_compra)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(
                    query_detalle,
                    (item.cantidad, item.subtotal, item.id_producto, new_compra_id),
                )

            conn.commit()
            return True, f"¡Venta #{new_compra_id} registrada con éxito!"

        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error en la transacción: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_resumen_df(self) -> pd.DataFrame:
        if not self._tiene_conexion():
            return pd.DataFrame()

        query = """
        SELECT
            c.id_compra,
            c.Fecha_hora AS Fecha,
            COALESCE(SUM(dc.Subtotal), 0) AS Monto_total,
            CONCAT(e.Apellido, ', ', e.Nombre) AS Empleado
        FROM Compra c
        LEFT JOIN Detalle_Compra dc ON dc.id_compra = c.id_compra
        JOIN Empleado e ON c.id_empleado = e.id_empleado
        GROUP BY c.id_compra, c.Fecha_hora, e.Apellido, e.Nombre
        ORDER BY c.Fecha_hora DESC, c.id_compra DESC;
        """
        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            st.error(f"Error al consultar el historial de ventas: {e}")
            return pd.DataFrame()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_detalles_df(self, id_compra: int) -> pd.DataFrame:
        if not self._tiene_conexion():
            return pd.DataFrame()

        query = """
        SELECT
            dc.Cantidad,
            p.Nombre AS Producto,
            m.nombre_marca AS Marca,
            p.Modelo,
            dc.Subtotal
        FROM Detalle_Compra dc
        JOIN Producto p ON dc.id_producto = p.id_producto
        LEFT JOIN Marca m ON p.id_marca = m.id_marca
        WHERE dc.id_compra = %s;
        """
        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (id_compra,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            st.error(f"Error al consultar detalles de la venta #{id_compra}: {e}")
            return pd.DataFrame()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

