from __future__ import annotations

from contextlib import contextmanager
from mysql.connector import pooling
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from src.core.config import Config, settings


class Base(DeclarativeBase):
    """Clase base declarativa para los modelos SQLAlchemy 2.0."""
    pass


engine = create_engine(
    settings.get_database_url(),
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


@contextmanager
def get_session():
    """
    Context Manager transaccional para sesiones SQLAlchemy:
    - commit() si todo sale bien
    - rollback() si ocurre una excepción
    - close() al finalizar
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection() -> bool:
    """Prueba rápida de conectividad con MySQL."""
    with engine.connect() as connection:
        return connection.execute(text("SELECT 1")).scalar_one() == 1


class DatabaseConnection:
    """
    Singleton para el pool de conexiones directo de mysql.connector
    (mantenido para compatibilidad con conexion.py).
    """

    _instance = None
    _pool = None

    def __new__(cls, config: Config = settings):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._inicializar_pool(config)
        return cls._instance

    def _inicializar_pool(self, config: Config) -> None:
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
                self._pool = None

    def get_pool(self):
        return self._pool

    def get_connection(self):
        if self._pool is None:
            raise ConnectionError("El pool de conexiones no está disponible.")
        return self._pool.get_connection()
