import streamlit as st
from mysql.connector import pooling
from core.config import Config, settings


class DatabaseConnection:
    """
    Gestiona el pool de conexiones a MySQL aplicando el patrón Singleton.
    Garantiza que exista una única instancia del pool en toda la aplicación.
    """

    _instance = None
    _pool = None

    def __new__(cls, config: Config = settings):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._inicializar_pool(config)
        return cls._instance

    def _inicializar_pool(self, config: Config) -> None:
        """Método privado para inicializar el pool de conexiones."""
        if self._pool is None:
            try:
                db_params = config.get_db_params()
                self._pool = pooling.MySQLConnectionPool(
                    pool_name="streamlit_pool",
                    pool_size=5,
                    **db_params
                )
            except Exception as e:
                print(f"Error al crear el pool de MySQL: {e}")
                st.error(f"Error de conexión a la base de datos: {e}")
                self._pool = None

    def get_pool(self):
        """Retorna la instancia activa del pool de conexiones."""
        return self._pool

    def get_connection(self):
        """Obtiene una conexión individual desde el pool."""
        if self._pool is None:
            raise ConnectionError("El pool de conexiones no está disponible.")
        return self._pool.get_connection()

