from typing import Optional
import streamlit as st
import pandas as pd
from models.producto import Producto
from repositories.base_repository import BaseRepository


class ProductoRepository(BaseRepository):
    """
    Repositorio encargado de las operaciones CRUD y consultas de inventario sobre Producto y Marca.
    """

    def _obtener_o_crear_marca(self, nombre_marca: Optional[str]) -> Optional[int]:
        if not self._tiene_conexion() or not nombre_marca:
            return None

        nombre = nombre_marca.strip()
        if not nombre:
            return None

        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_marca FROM Marca WHERE nombre_marca = %s", (nombre,))
            result = cursor.fetchone()
            if result:
                return result[0]

            cursor.execute("INSERT INTO Marca (nombre_marca) VALUES (%s)", (nombre,))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            if conn:
                conn.rollback()
            st.error(f"Error al gestionar la marca: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_todos_df(self) -> pd.DataFrame:
        if not self._tiene_conexion():
            st.warning("No hay pool de conexión.")
            return pd.DataFrame()

        query = """
        SELECT 
            p.id_producto, p.Nombre, m.nombre_marca AS Marca, p.Modelo, p.Memoria_VRAM,
            p.Precio, p.Stock, pr.Nombre AS Proveedor
        FROM Producto p
        LEFT JOIN Proveedor pr ON p.id_proveedor = pr.id_proveedor
        LEFT JOIN Marca m ON p.id_marca = m.id_marca
        ORDER BY m.nombre_marca, p.Modelo;
        """
        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            df = pd.DataFrame(results)
            if not df.empty:
                df.columns = [
                    "ID", "Nombre", "Marca", "Modelo",
                    "VRAM", "Precio", "Stock", "Proveedor"
                ]
            return df
        except Exception as e:
            st.error(f"Error al consultar los productos: {e}")
            return pd.DataFrame()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_disponibles_df(self) -> pd.DataFrame:
        if not self._tiene_conexion():
            return pd.DataFrame()

        query = """
        SELECT p.id_producto, p.Nombre, m.nombre_marca AS Marca, p.Modelo, p.Precio, p.Stock
        FROM Producto p
        LEFT JOIN Marca m ON p.id_marca = m.id_marca
        WHERE p.Stock > 0
        ORDER BY m.nombre_marca, p.Modelo;
        """
        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            st.error(f"Error al consultar productos disponibles: {e}")
            return pd.DataFrame()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_stock_bajo_df(self, umbral: int = 10) -> pd.DataFrame:
        if not self._tiene_conexion():
            return pd.DataFrame()

        query = """
            SELECT p.Nombre, m.nombre_marca AS Marca, p.Modelo, p.Stock
            FROM Producto p
            LEFT JOIN Marca m ON p.id_marca = m.id_marca
            WHERE p.Stock <= %s AND p.Stock > 0
            ORDER BY p.Stock ASC;
        """
        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (umbral,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            st.error(f"Error al consultar stock bajo: {e}")
            return pd.DataFrame()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def crear(self, producto: Producto) -> bool:
        if not self._tiene_conexion():
            return False

        id_marca = self._obtener_o_crear_marca(producto.marca)
        if id_marca is None and producto.marca:
            return False

        query = """
            INSERT INTO Producto
                (Nombre, Modelo, Memoria_VRAM, Precio, Stock, id_marca, id_proveedor)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            producto.nombre,
            producto.modelo,
            producto.vram,
            producto.precio,
            producto.stock,
            id_marca,
            producto.id_proveedor,
        )
        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            st.error(f"Error al añadir el producto: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def actualizar(self, producto: Producto) -> bool:
        if not self._tiene_conexion():
            return False

        id_marca = self._obtener_o_crear_marca(producto.marca)
        if id_marca is None and producto.marca:
            return False

        query = """
            UPDATE Producto
            SET
                Nombre = %s,
                Modelo = %s,
                Memoria_VRAM = %s,
                Precio = %s,
                Stock = %s,
                id_marca = %s,
                id_proveedor = %s
            WHERE
                id_producto = %s
        """
        data = (
            producto.nombre,
            producto.modelo,
            producto.vram,
            producto.precio,
            producto.stock,
            id_marca,
            producto.id_proveedor,
            producto.id_producto,
        )
        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            st.error(f"Error al actualizar el producto: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def eliminar(self, id_producto: int) -> tuple[bool, str]:
        if not self._tiene_conexion():
            return False, "Error de conexión"
        if not id_producto:
            return False, "No se seleccionó un ID"

        query = "DELETE FROM Producto WHERE id_producto = %s"
        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, (id_producto,))
            if cursor.rowcount == 1:
                conn.commit()
                return True, "¡Producto eliminado con éxito!"
            else:
                conn.rollback()
                return False, "No se encontró ningún producto con ese ID."
        except Exception as e:
            if conn:
                conn.rollback()
            if "foreign key constraint" in str(e).lower():
                return False, "Error: No se puede eliminar. El producto ya está asociado a una o más ventas."
            return False, f"Error inesperado al eliminar el producto: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

