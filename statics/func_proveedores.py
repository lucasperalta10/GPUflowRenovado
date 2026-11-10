import streamlit as st
import pandas as pd
from conexion import get_connection_pool


def proveedores(pool):
    if pool is None: return pd.DataFrame()
    
    query = "SELECT id_proveedor, Nombre FROM Proveedor ORDER BY Nombre;"
    
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Error al consultar los proveedores: {e}")
        return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()
def añadir_proveedor(pool, nombre, direccion, email):
    if pool is None: return False, "No hay conexión con la base de datos."

    query = """
        INSERT INTO Proveedor (Nombre, Direccion, Correo_Electronico)
        VALUES (%s, %s, %s)
    """
    data = (nombre, direccion, email if email else None)
    
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        conn.commit()
        return True, f"¡Proveedor '{nombre}' registrado con éxito!"
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        if "Duplicate entry" in str(e):
            return False, f"Error: Ya existe un proveedor con el correo electrónico '{email}'."
        else:
            return False, f"Error al añadir el proveedor: {e}"
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()
def actualizar_proveedor(pool, id_proveedor, nombre, direccion, email):
    """
    Actualiza un proveedor existente en la base de datos.
    """
    if pool is None: return False, "Error de conexión"

    query = """
        UPDATE Proveedor
        SET 
            Nombre = %s,
            Direccion = %s,
            Correo_Electronico = %s
        WHERE 
            id_proveedor = %s
    """
    data = (nombre, direccion, email if email else None, id_proveedor)
    
    conn = None
    cursor = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        conn.commit()
        return True, "¡Proveedor actualizado con éxito!"
    except Exception as e:
        if conn: conn.rollback()
        if "Duplicate entry" in str(e):
            return False, f"Error: Ya existe un proveedor con el correo electrónico '{email}'."
        else:
            return False, f"Error al actualizar el proveedor: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
def eliminar_proveedor(pool, id_proveedor):
    """
    Elimina un proveedor de la base de datos usando su ID.
    Maneja la restricción de clave externa si el proveedor ya está en uso.
    """
    if pool is None: return False, "Error de conexión"
    if not id_proveedor: return False, "No se seleccionó un ID"
        
    query = "DELETE FROM Proveedor WHERE id_proveedor = %s"
    data = (id_proveedor,)
    
    conn = None
    cursor = None
    
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        
        if cursor.rowcount == 1:
            conn.commit()
            return True, "¡Proveedor eliminado con éxito!"
        else:
            conn.rollback()
            return False, "No se encontró ningún proveedor con ese ID."
        
    except Exception as e:
        if conn: conn.rollback()
        
        if "foreign key constraint" in str(e).lower():
            return False, "Error: No se puede eliminar. El proveedor está asociado a uno o más productos."
        else:
            return False, f"Error inesperado al eliminar el proveedor: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()