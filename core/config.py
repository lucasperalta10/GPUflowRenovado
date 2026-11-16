import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Clase de configuración centralizada.
    Encapsula la lectura de variables de entorno (.env).
    """

    def __init__(self):
        self.db_host: str = os.getenv("DB_HOST", "localhost")
        self.db_user: str = os.getenv("DB_USER", "root")
        self.db_password: str = os.getenv("DB_PASSWORD", os.getenv("DB_PASS", ""))
        self.db_name: str = os.getenv("DB_NAME", "db_almacenrtx")
        self.db_port: int = int(os.getenv("DB_PORT", "3306"))
        self.app_name: str = os.getenv("APP_NAME", "GPUflow")
        self.app_env: str = os.getenv("APP_ENV", "local")

    def get_db_params(self) -> dict:
        """Retorna un diccionario con los parámetros de conexión para MySQL."""
        return {
            "host": self.db_host,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "port": self.db_port,
        }


# Instancia global de configuración
settings = Config()

