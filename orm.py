"""
orm.py - Punto de entrada raíz para el ORM de GPUflow.
Reexporta todas las clases y funciones de core.orm.
"""

from src.core.orm import (
    Base,
    engine,
    SessionLocal,
    get_db_session,
    crear_tablas,
    UsuarioORM,
    CargoORM,
    EmpleadoORM,
    ProveedorORM,
    MarcaORM,
    ProductoORM,
    CompraORM,
    DetalleCompraORM,
)

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db_session",
    "crear_tablas",
    "UsuarioORM",
    "CargoORM",
    "EmpleadoORM",
    "ProveedorORM",
    "MarcaORM",
    "ProductoORM",
    "CompraORM",
    "DetalleCompraORM",
]
