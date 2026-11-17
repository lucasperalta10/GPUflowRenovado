"""
core/orm.py - Mapeo Objeto-Relacional (ORM) con SQLAlchemy 2.0 para GPUflow.

Utiliza DeclarativeBase, Mapped y mapped_column según el estándar SQLAlchemy 2.0.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import DateTime, DECIMAL, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, SessionLocal, engine, get_session


# Alias para compatibilidad
get_db_session = get_session


class UsuarioORM(Base):
    """Mapeo de la tabla 'usuario'."""
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str | None] = mapped_column(String(20), default="admin")

    def __repr__(self) -> str:
        return f"<UsuarioORM(id={self.id_usuario}, username='{self.username}', rol='{self.rol}')>"


class CargoORM(Base):
    """Mapeo de la tabla 'cargo'."""
    __tablename__ = "cargo"

    id_cargo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_cargo: Mapped[str] = mapped_column(String(80), nullable=False)

    empleados: Mapped[List["EmpleadoORM"]] = relationship(back_populates="cargo")

    def __repr__(self) -> str:
        return f"<CargoORM(id={self.id_cargo}, cargo='{self.nombre_cargo}')>"


class EmpleadoORM(Base):
    """Mapeo de la tabla 'empleado'."""
    __tablename__ = "empleado"

    id_empleado: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    Apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    Correo_Electronico: Mapped[str | None] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    direccion: Mapped[str | None] = mapped_column(String(150))
    id_cargo: Mapped[int | None] = mapped_column(ForeignKey("cargo.id_cargo"))
    id_ciudad: Mapped[int | None] = mapped_column(Integer)
    id_empresa: Mapped[int | None] = mapped_column(Integer)

    cargo: Mapped["CargoORM | None"] = relationship(back_populates="empleados")
    compras_realizadas: Mapped[List["CompraORM"]] = relationship(back_populates="empleado")

    @property
    def nombre_completo(self) -> str:
        return f"{self.Apellido}, {self.Nombre}"

    def __repr__(self) -> str:
        return f"<EmpleadoORM(id={self.id_empleado}, nombre='{self.nombre_completo}')>"


class ProveedorORM(Base):
    """Mapeo de la tabla 'proveedor'."""
    __tablename__ = "proveedor"

    id_proveedor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    Direccion: Mapped[str | None] = mapped_column(String(150))
    id_ciudad: Mapped[int | None] = mapped_column(Integer)
    Correo_Electronico: Mapped[str | None] = mapped_column(String(100), unique=True)

    productos: Mapped[List["ProductoORM"]] = relationship(back_populates="proveedor")

    def __repr__(self) -> str:
        return f"<ProveedorORM(id={self.id_proveedor}, nombre='{self.Nombre}')>"


class MarcaORM(Base):
    """Mapeo de la tabla 'marca'."""
    __tablename__ = "marca"

    id_marca: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_marca: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    productos: Mapped[List["ProductoORM"]] = relationship(back_populates="marca")

    def __repr__(self) -> str:
        return f"<MarcaORM(id={self.id_marca}, marca='{self.nombre_marca}')>"


class ProductoORM(Base):
    """Mapeo de la tabla 'producto' (Tarjetas Gráficas)."""
    __tablename__ = "producto"

    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    Modelo: Mapped[str | None] = mapped_column(String(50))
    Memoria_VRAM: Mapped[str | None] = mapped_column(String(50))
    Precio: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    Stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    id_marca: Mapped[int | None] = mapped_column(ForeignKey("marca.id_marca"))
    id_tipo_memoria: Mapped[int | None] = mapped_column(Integer)
    id_proveedor: Mapped[int | None] = mapped_column(ForeignKey("proveedor.id_proveedor"))

    marca: Mapped["MarcaORM | None"] = relationship(back_populates="productos")
    proveedor: Mapped["ProveedorORM | None"] = relationship(back_populates="productos")
    detalles: Mapped[List["DetalleCompraORM"]] = relationship(back_populates="producto")

    def __repr__(self) -> str:
        return f"<ProductoORM(id={self.id_producto}, nombre='{self.Nombre}', stock={self.Stock})>"


class CompraORM(Base):
    """Mapeo de la tabla 'compra' (Cabecera de venta)."""
    __tablename__ = "compra"

    id_compra: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Fecha_hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)
    id_empleado: Mapped[int] = mapped_column(ForeignKey("empleado.id_empleado"), nullable=False)

    empleado: Mapped["EmpleadoORM"] = relationship(back_populates="compras_realizadas")
    detalles: Mapped[List["DetalleCompraORM"]] = relationship(
        back_populates="compra",
        cascade="all, delete-orphan",
    )

    @property
    def monto_total(self) -> float:
        return sum(float(d.Subtotal) for d in self.detalles)

    def __repr__(self) -> str:
        return f"<CompraORM(id={self.id_compra}, fecha='{self.Fecha_hora}')>"


class DetalleCompraORM(Base):
    """Mapeo de la tabla 'detalle_compra' (Ítems vendidos)."""
    __tablename__ = "detalle_compra"

    id_detalle_compra: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    Subtotal: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    id_producto: Mapped[int] = mapped_column(ForeignKey("producto.id_producto"), nullable=False)
    id_compra: Mapped[int] = mapped_column(ForeignKey("compra.id_compra"), nullable=False)

    compra: Mapped["CompraORM"] = relationship(back_populates="detalles")
    producto: Mapped["ProductoORM"] = relationship(back_populates="detalles")

    def __repr__(self) -> str:
        return f"<DetalleCompraORM(id={self.id_detalle_compra}, prod_id={self.id_producto}, cant={self.Cantidad})>"


def crear_tablas():
    """Crea todas las tablas mapeadas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)
