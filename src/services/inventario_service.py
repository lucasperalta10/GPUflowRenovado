from typing import Optional
import pandas as pd
from sqlalchemy.exc import IntegrityError
from src.core.database import get_session
from src.models.empleado import Empleado
from src.models.producto import Producto
from src.models.proveedor import Proveedor
from src.models.venta import ItemVenta, Venta
from src.repositories.empleado_repository import EmpleadoRepository
from src.repositories.producto_repository import ProductoRepository
from src.repositories.proveedor_repository import ProveedorRepository
from src.repositories.venta_repository import VentaRepository


class ProveedorService:
    """Servicio de reglas de negocio para Proveedores."""

    def listar(self) -> pd.DataFrame:
        with get_session() as session:
            return ProveedorRepository(session).obtener_todos_df()

    def listar_completos(self) -> pd.DataFrame:
        with get_session() as session:
            return ProveedorRepository(session).obtener_todos_completos_df()

    def obtener_por_id(self, id_proveedor: int) -> Optional[Proveedor]:
        with get_session() as session:
            return ProveedorRepository(session).obtener_por_id(id_proveedor)

    def crear_proveedor(self, nombre: str, direccion: str = "", email: str = "") -> tuple[bool, str]:
        proveedor = Proveedor(nombre=nombre, direccion=direccion, email=email)
        if not proveedor.tiene_datos_validos():
            return False, "El campo 'Nombre' es obligatorio."
        try:
            with get_session() as session:
                ProveedorRepository(session).crear(proveedor)
            return True, f"¡Proveedor '{proveedor.nombre}' registrado con éxito!"
        except IntegrityError:
            return False, f"Error: Ya existe un proveedor con el correo electrónico '{proveedor.email}'."
        except Exception as exc:
            return False, f"Error al añadir el proveedor: {exc}"

    def actualizar_proveedor(
        self, id_proveedor: int, nombre: str, direccion: str = "", email: str = ""
    ) -> tuple[bool, str]:
        proveedor = Proveedor(
            id_proveedor=id_proveedor,
            nombre=nombre,
            direccion=direccion,
            email=email,
        )
        if not proveedor.tiene_datos_validos():
            return False, "El campo 'Nombre' es obligatorio."
        try:
            with get_session() as session:
                actualizado = ProveedorRepository(session).actualizar(proveedor)
                if actualizado is None:
                    return False, "No se encontró el proveedor."
            return True, "¡Proveedor actualizado con éxito!"
        except IntegrityError:
            return False, f"Error: Ya existe un proveedor con el correo electrónico '{proveedor.email}'."
        except Exception as exc:
            return False, f"Error al actualizar el proveedor: {exc}"

    def eliminar_proveedor(self, id_proveedor: int) -> tuple[bool, str]:
        if not id_proveedor:
            return False, "No se seleccionó un ID."
        try:
            with get_session() as session:
                eliminado = ProveedorRepository(session).eliminar(id_proveedor)
                if not eliminado:
                    return False, "No se encontró ningún proveedor con ese ID."
            return True, "¡Proveedor eliminado con éxito!"
        except IntegrityError:
            return False, "Error: No se puede eliminar. El proveedor está asociado a uno o más productos."
        except Exception as exc:
            return False, f"Error inesperado al eliminar el proveedor: {exc}"


class EmpleadoService:
    """Servicio de reglas de negocio para Empleados."""

    def listar(self) -> pd.DataFrame:
        with get_session() as session:
            return EmpleadoRepository(session).obtener_todos_df()

    def crear_empleado(self, nombre: str, apellido: str, cargo: Optional[str]) -> tuple[bool, str]:
        empleado = Empleado(nombre=nombre, apellido=apellido, cargo=cargo)
        if not empleado.tiene_datos_validos():
            return False, "Los campos Nombre y Apellido son obligatorios."
        try:
            with get_session() as session:
                EmpleadoRepository(session).crear(empleado)
            return True, f"¡Empleado '{empleado.nombre} {empleado.apellido}' registrado con éxito!"
        except Exception as exc:
            return False, f"Error al añadir el empleado: {exc}"

    def actualizar_empleado(
        self, id_empleado: int, nombre: str, apellido: str, cargo: Optional[str]
    ) -> tuple[bool, str]:
        empleado = Empleado(
            id_empleado=id_empleado,
            nombre=nombre,
            apellido=apellido,
            cargo=cargo,
        )
        if not empleado.tiene_datos_validos():
            return False, "Los campos Nombre y Apellido son obligatorios."
        try:
            with get_session() as session:
                actualizado = EmpleadoRepository(session).actualizar(empleado)
                if actualizado is None:
                    return False, "No se encontró el empleado."
            return True, "¡Empleado actualizado con éxito!"
        except Exception as exc:
            return False, f"Error al actualizar el empleado: {exc}"


class ProductoService:
    """Servicio de reglas de negocio para Productos e Inventario."""

    def listar(self) -> pd.DataFrame:
        with get_session() as session:
            return ProductoRepository(session).obtener_todos_df()

    def listar_disponibles(self) -> pd.DataFrame:
        with get_session() as session:
            return ProductoRepository(session).obtener_disponibles_df()

    def listar_stock_bajo(self, umbral: int = 10) -> pd.DataFrame:
        with get_session() as session:
            return ProductoRepository(session).obtener_stock_bajo_df(umbral=umbral)

    def crear_producto(
        self,
        nombre: str,
        marca: str,
        modelo: str,
        vram: str,
        precio: float,
        stock: int,
        id_proveedor: int,
    ) -> tuple[bool, str]:
        try:
            producto = Producto(
                nombre=nombre,
                marca=marca,
                modelo=modelo,
                vram=vram,
                precio=precio,
                stock=stock,
                id_proveedor=id_proveedor,
            )
            if not producto.nombre or not producto.marca or not producto.modelo:
                return False, "Por favor, rellene todos los campos obligatorios."
            with get_session() as session:
                ProductoRepository(session).crear(producto)
            return True, f"¡Producto '{producto.nombre}' añadido con éxito!"
        except ValueError as exc:
            return False, str(exc)
        except Exception as exc:
            return False, f"Error al añadir el producto: {exc}"

    def actualizar_producto(
        self,
        id_producto: int,
        nombre: str,
        marca: str,
        modelo: str,
        vram: str,
        precio: float,
        stock: int,
        id_proveedor: int,
    ) -> tuple[bool, str]:
        try:
            producto = Producto(
                id_producto=id_producto,
                nombre=nombre,
                marca=marca,
                modelo=modelo,
                vram=vram,
                precio=precio,
                stock=stock,
                id_proveedor=id_proveedor,
            )
            with get_session() as session:
                actualizado = ProductoRepository(session).actualizar(producto)
                if actualizado is None:
                    return False, "No se encontró el producto."
            return True, "¡Producto actualizado con éxito!"
        except ValueError as exc:
            return False, str(exc)
        except Exception as exc:
            return False, f"Error al actualizar el producto: {exc}"

    def eliminar_producto(self, id_producto: int) -> tuple[bool, str]:
        if not id_producto:
            return False, "No se seleccionó un ID."
        try:
            with get_session() as session:
                eliminado = ProductoRepository(session).eliminar(id_producto)
                if not eliminado:
                    return False, "No se encontró ningún producto con ese ID."
            return True, "¡Producto eliminado con éxito!"
        except IntegrityError:
            return False, "Error: No se puede eliminar. El producto ya está asociado a una o más ventas."
        except Exception as exc:
            return False, f"Error inesperado al eliminar el producto: {exc}"


class VentaService:
    """Servicio de reglas de negocio para el Módulo de Ventas."""

    def procesar_venta(self, id_empleado: int, cart: list[dict]) -> tuple[bool, str]:
        if not cart:
            return False, "El carrito está vacío."
        try:
            items = [ItemVenta.from_dict(item) for item in cart]
            venta = Venta(id_empleado=id_empleado, items=items)
            with get_session() as session:
                compra_id = VentaRepository(session).registrar_venta(venta)
            return True, f"¡Venta #{compra_id} registrada con éxito!"
        except ValueError as exc:
            return False, str(exc)
        except Exception as exc:
            return False, f"Error en la transacción: {exc}"

    def resumen_ventas(self) -> pd.DataFrame:
        with get_session() as session:
            return VentaRepository(session).obtener_resumen_df()

    def detalles_venta(self, id_compra: int) -> pd.DataFrame:
        with get_session() as session:
            return VentaRepository(session).obtener_detalles_df(id_compra)
