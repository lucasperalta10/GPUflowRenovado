from typing import Optional
from datetime import datetime
from models.base import EntidadBase


class ItemVenta(EntidadBase):
    """
    Representa una línea o ítem dentro de una venta (detalle).
    """

    def __init__(
        self,
        id_producto: int,
        nombre: str,
        marca: str,
        modelo: str,
        cantidad: int,
        precio_unitario: float,
    ):
        self.id_producto = id_producto
        self.nombre = nombre
        self.marca = marca
        self.modelo = modelo
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)

    @property
    def subtotal(self) -> float:
        """Calcula dinámicamente el subtotal del ítem."""
        return self.cantidad * self.precio_unitario

    @classmethod
    def from_dict(cls, data: dict) -> "ItemVenta":
        """Crea una instancia de ItemVenta a partir de un diccionario del carrito."""
        return cls(
            id_producto=data["ID"],
            nombre=data["Nombre"],
            marca=data.get("Marca", ""),
            modelo=data.get("Modelo", ""),
            cantidad=data["Cantidad"],
            precio_unitario=data.get("Precio_Unitario", data["Subtotal"] / data["Cantidad"]),
        )

    def to_dict(self) -> dict:
        return {
            "ID": self.id_producto,
            "Nombre": self.nombre,
            "Marca": self.marca,
            "Modelo": self.modelo,
            "Cantidad": self.cantidad,
            "Precio_Unitario": self.precio_unitario,
            "Subtotal": self.subtotal,
        }


class Venta(EntidadBase):
    """
    Representa una transacción de venta completa.
    Aplica Composición al contener una colección de objetos ItemVenta.
    """

    def __init__(
        self,
        id_empleado: int,
        items: Optional[list[ItemVenta]] = None,
        id_compra: Optional[int] = None,
        fecha_hora: Optional[str] = None,
    ):
        self.id_compra = id_compra
        self.id_empleado = id_empleado
        self.items: list[ItemVenta] = items if items is not None else []
        self.fecha_hora = fecha_hora or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def agregar_item(self, item: ItemVenta) -> None:
        """Agrega un ítem al detalle de la venta."""
        self.items.append(item)

    @property
    def monto_total(self) -> float:
        """Suma los subtotales de todos los ítems que componen la venta."""
        return sum(item.subtotal for item in self.items)

    def esta_vacia(self) -> bool:
        return len(self.items) == 0

    def to_dict(self) -> dict:
        return {
            "id_compra": self.id_compra,
            "id_empleado": self.id_empleado,
            "fecha_hora": self.fecha_hora,
            "monto_total": self.monto_total,
            "items": [item.to_dict() for item in self.items],
        }

