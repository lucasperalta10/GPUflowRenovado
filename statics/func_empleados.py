import streamlit as st
import pandas as pd
from conexion import get_connection_pool


def _obtener_o_crear_cargo(pool, nombre_cargo):
    if pool is None or not nombre_cargo:
        return None

    nombre = nombre_cargo.strip()
    if not nombre:
        return None

    conn = None
    cursor = None
    try:
        conn = pool.get_connection()
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


def empleados(pool):
    if pool is None:
        return pd.DataFrame()

    query = "SELECT e.id_empleado, e.Nombre, e.Apellido, c.nombre_cargo AS Cargo FROM Empleado e LEFT JOIN Cargo c ON e.id_cargo = c.id_cargo ORDER BY e.Apellido;"

    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        df = pd.DataFrame(results)
        df.columns = ['ID', 'Nombre', 'Apellido', 'Cargo']
        return df
    except Exception as e:
        st.error(f"Error al consultar los empleados: {e}")
        return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def añadir_empleado(pool, nombre, apellido, cargo):
    if pool is None:
        return False, "No hay conexión con la base de datos."

    if not nombre or not apellido:
        return False, "Los campos Nombre y Apellido son obligatorios."

    id_cargo = _obtener_o_crear_cargo(pool, cargo)
    if id_cargo is None and cargo:
        return False, "Error al asignar o crear el cargo."

    query = "INSERT INTO Empleado (Nombre, Apellido, id_cargo, password) VALUES (%s, %s, %s, '')"
    data = (nombre, apellido, id_cargo)

    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        conn.commit()
        return True, f"¡Empleado '{nombre} {apellido}' registrado con éxito!"
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        return False, f"Error al añadir el empleado: {e}"
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def actualizar_empleado(pool, id_empleado, nombre, apellido, cargo):
    """
    Actualiza un empleado existente en la base de datos.
    """
    if pool is None:
        return False, "Error de conexión"

    id_cargo = _obtener_o_crear_cargo(pool, cargo)
    if id_cargo is None and cargo:
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
    data = (nombre, apellido, id_cargo, id_empleado)

    conn = None
    cursor = None
    try:
        conn = pool.get_connection()
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