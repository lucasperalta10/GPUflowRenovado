from typing import Optional
import streamlit as st
from models.usuario import Usuario
from repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    """
    Repositorio encargado de las operaciones SQL sobre la tabla Usuario.
    """

    def autenticar(self, username: str, password: str) -> Optional[Usuario]:
        """Verifica las credenciales y retorna un objeto Usuario si son válidas."""
        if not self._tiene_conexion():
            return None

        query = "SELECT * FROM Usuario WHERE username = %s AND password = %s"
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (username, password))
            row = cursor.fetchone()
            if row:
                return Usuario(
                    id_usuario=row.get("id_usuario"),
                    username=row.get("username", ""),
                    password=row.get("password", ""),
                    rol=row.get("rol", "Admin"),
                )
            return None
        except Exception as e:
            st.error(f"Error de login: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def crear(self, usuario: Usuario) -> bool:
        """Inserta un nuevo objeto Usuario en la base de datos."""
        if not self._tiene_conexion():
            return False

        query = "INSERT INTO Usuario (username, password, rol) VALUES (%s, %s, %s)"
        conn = None
        cursor = None

        try:
            conn = self._obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(query, (usuario.username, usuario.password, usuario.rol))
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            if "Duplicate entry" in str(e):
                st.warning("Ese nombre de usuario ya existe.")
            else:
                st.error(f"Error al crear usuario: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

