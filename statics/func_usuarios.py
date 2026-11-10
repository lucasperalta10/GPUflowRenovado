import streamlit as st
from conexion import get_connection_pool


def login_usuario(pool, username, password):
    """Verifica si el usuario y la contraseña coinciden en la tabla Usuario."""
    if pool is None:
        return None

    query = "SELECT * FROM Usuario WHERE username = %s AND password = %s"

    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        return user
    except Exception as e:
        st.error(f"Error de login: {e}")
        return None
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def crear_usuario(pool, username, password):
    """Registra un nuevo usuario con contraseña en texto plano."""
    if pool is None:
        return False

    query = "INSERT INTO Usuario (username, password, rol) VALUES (%s, %s, 'Admin')"

    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (username, password))
        conn.commit()
        return True
    except Exception as e:
        if "Duplicate entry" in str(e):
            st.warning("Ese nombre de usuario ya existe.")
        else:
            st.error(f"Error al crear usuario: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()