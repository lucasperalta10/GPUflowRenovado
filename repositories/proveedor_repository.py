import streamlit as st
import pandas as pd
from models.proveedor import Proveedor
from repositories.base_repository import BaseRepository


class ProveedorRepository(BaseRepository):
    """
    Repositorio encargado de las operaciones CRUD sobre la entidad Proveedor.
    """

    def obtener_todos_df(self) -> pd.DataFrame:
        if not self._tiene_conexion():
            return pd.DataFrame()

        query = "SELECT id_proveedor, Nombre FROM Proveedor ORDER BY Nombre;"
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return pd.DataFrame(results)
        except Exception as e:
            st.error(f"Error al consultar los proveedores: {e}")
            return pd.DataFrame()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_todos_completos_df(self) -> pd.DataFrame:
        """Retorna el listado completo de proveedores con dirección y correo."""
        if not self._tiene_conexion():
            return pd.DataFrame()

        query = "SELECT id_proveedor, Nombre, Direccion, Correo_Electronico FROM Proveedor ORDER BY Nombre;"
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            st.error(f"Error al cargar datos completos de proveedores: {e}")
            return pd.DataFrame()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_por_id(self, id_proveedor: int):
        """Obtiene un objeto Proveedor por su ID."""
        if not self._tiene_conexion():
            return None

        query = "SELECT id_proveedor, Nombre, Direccion, Correo_Electronico FROM Proveedor WHERE id_proveedor = %s"
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (id_proveedor,))
            row = cursor.fetchone()
            if row:
                return Proveedor(
                    id_proveedor=row.get("id_proveedor"),
                    nombre=row.get("Nombre", ""),
                    direccion=row.get("Direccion") or "",
                    email=row.get("Correo_Electronico") or "",
                )
            return None
        except Exception as e:
            st.error(f"Error al obtener proveedor #{id_proveedor}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def crear(self, proveedor: Proveedor) -> tuple[bool, str]:
        if not self._tiene_conexion():
            return False, "No hay conexión con la base de datos."

        if not proveedor.tiene_datos_validos():
            return False, "El campo 'Nombre' es obligatorio."

        query = """
            INSERT INTO Proveedor (Nombre, Direccion, Correo_Electronico)
            VALUES (%s, %s, %s)
        """
        data = (proveedor.nombre, proveedor.direccion, proveedor.email)
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            return True, f"¡Proveedor '{proveedor.nombre}' registrado con éxito!"
        except Exception as e:
            if conn:
                conn.rollback()
            if "Duplicate entry" in str(e):
                return False, f"Error: Ya existe un proveedor con el correo electrónico '{proveedor.email}'."
            return False, f"Error al añadir el proveedor: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def actualizar(self, proveedor: Proveedor) -> tuple[bool, str]:
        if not self._tiene_conexion():
            return False, "Error de conexión"

        query = """
            UPDATE Proveedor
            SET
                Nombre = %s,
                Direccion = %s,
                Correo_Electronico = %s
            WHERE
                id_proveedor = %s
        """
        data = (proveedor.nombre, proveedor.direccion, proveedor.email, proveedor.id_proveedor)
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            return True, "¡Proveedor actualizado con éxito!"
        except Exception as e:
            if conn:
                conn.rollback()
            if "Duplicate entry" in str(e):
                return False, f"Error: Ya existe un proveedor con el correo electrónico '{proveedor.email}'."
            return False, f"Error al actualizar el proveedor: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def eliminar(self, id_proveedor: int) -> tuple[bool, str]:
        if not self._tiene_conexion():
            return False, "Error de conexión"
        if not id_proveedor:
            return False, "No se seleccionó un ID"

        query = "DELETE FROM Proveedor WHERE id_proveedor = %s"
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, (id_proveedor,))
            if cursor.rowcount == 1:
                conn.commit()
                return True, "¡Proveedor eliminado con éxito!"
            else:
                conn.rollback()
                return False, "No se encontró ningún proveedor con ese ID."
        except Exception as e:
            if conn:
                conn.rollback()
            if "foreign key constraint" in str(e).lower():
                return False, "Error: No se puede eliminar. El proveedor está asociado a uno o más productos."
            return False, f"Error inesperado al eliminar el proveedor: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

