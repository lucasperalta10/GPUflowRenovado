from typing import Optional
import streamlit as st
import pandas as pd
from models.empleado import Empleado
from repositories.base_repository import BaseRepository


class EmpleadoRepository(BaseRepository):
    """
    Repositorio encargado de las operaciones CRUD sobre Empleado y Cargo.
    """

    def _obtener_o_crear_cargo(self, nombre_cargo: Optional[str]) -> Optional[int]:
        if not self._tiene_conexion() or not nombre_cargo:
            return None

        nombre = nombre_cargo.strip()
        if not nombre or nombre == "(Ninguno)":
            return None

        conn = None
        cursor = None
        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_cargo FROM Cargo WHERE nombre_cargo = %s", (nombre,))
            result = cursor.fetchone()
            if result:
                return result[0]

            cursor.execute("INSERT INTO Cargo (nombre_cargo) VALUES (%s)", (nombre,))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            if conn:
                conn.rollback()
            st.error(f"Error al gestionar el cargo: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_todos_df(self) -> pd.DataFrame:
        if not self._tiene_conexion():
            return pd.DataFrame()

        query = """
            SELECT e.id_empleado, e.Nombre, e.Apellido, c.nombre_cargo AS Cargo
            FROM Empleado e
            LEFT JOIN Cargo c ON e.id_cargo = c.id_cargo
            ORDER BY e.Apellido;
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
                df.columns = ["ID", "Nombre", "Apellido", "Cargo"]
            return df
        except Exception as e:
            st.error(f"Error al consultar los empleados: {e}")
            return pd.DataFrame()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def crear(self, empleado: Empleado) -> tuple[bool, str]:
        if not self._tiene_conexion():
            return False, "No hay conexión con la base de datos."

        if not empleado.tiene_datos_validos():
            return False, "Los campos Nombre y Apellido son obligatorios."

        id_cargo = self._obtener_o_crear_cargo(empleado.cargo)
        if id_cargo is None and empleado.cargo:
            return False, "Error al asignar o crear el cargo."

        query = "INSERT INTO Empleado (Nombre, Apellido, id_cargo, password) VALUES (%s, %s, %s, %s)"
        data = (empleado.nombre, empleado.apellido, id_cargo, empleado.password)
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            return True, f"¡Empleado '{empleado.nombre} {empleado.apellido}' registrado con éxito!"
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error al añadir el empleado: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def actualizar(self, empleado: Empleado) -> tuple[bool, str]:
        if not self._tiene_conexion():
            return False, "Error de conexión"

        id_cargo = self._obtener_o_crear_cargo(empleado.cargo)
        if id_cargo is None and empleado.cargo:
            return False, "No se pudo asignar el cargo."

        query = """
            UPDATE Empleado
            SET
                Nombre = %s,
                Apellido = %s,
                id_cargo = %s
            WHERE
                id_empleado = %s
        """
        data = (empleado.nombre, empleado.apellido, id_cargo, empleado.id_empleado)
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            return True, "¡Empleado actualizado con éxito!"
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error al actualizar el empleado: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

