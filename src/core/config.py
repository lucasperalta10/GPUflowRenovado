from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Configuración inmutable de la aplicación cargada desde variables de entorno (.env).
    """

    app_name: str = os.getenv("APP_NAME", "GPUflow")
    app_env: str = os.getenv("APP_ENV", "local")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", os.getenv("DB_PASS", ""))
    db_name: str = os.getenv("DB_NAME", "db_almacenrtx")
    database_url: str = os.getenv("DATABASE_URL", "")

    def get_database_url(self) -> str:
        """Retorna DATABASE_URL si está definida, o la construye con los parámetros MySQL."""
        if self.database_url:
            return self.database_url
        return (
            f"mysql+mysqlconnector://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def get_db_params(self) -> dict:
        """Retorna un diccionario con los parámetros de conexión para MySQL."""
        return {
            "host": self.db_host,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "port": self.db_port,
        }


# Alias de compatibilidad
Config = Settings
settings = Settings()

if not settings.get_database_url():
    raise RuntimeError(
        "No encontramos configuración de base de datos. "
        "Revisemos el archivo .env."
    )
