from typing import Optional
from src.models.base import EntidadBase


class Producto(EntidadBase):
    """
    Representa una tarjeta gráfica (GPU) en el inventario.
    Aplica Encapsulamiento sobre atributos críticos como precio y stock.
    """

    def __init__(
        self,
        nombre: str,
        marca: str,
        modelo: str,
        vram: Optional[str],
        precio: float,
        stock: int,
        id_proveedor: Optional[int] = None,
        id_producto: Optional[int] = None,
        proveedor_nombre: Optional[str] = None,
    ):
        self.id_producto = id_producto
        self.nombre = nombre.strip() if nombre else ""
        self.marca = marca.strip() if marca else ""
        self.modelo = modelo.strip() if modelo else ""
        self.vram = vram.strip() if vram else ""
        self._precio = 0.0
        self._stock = 0
        self.precio = precio
        self.stock = stock
        self.id_proveedor = id_proveedor
        self.proveedor_nombre = proveedor_nombre

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float) -> None:
        if float(valor) < 0:
            raise ValueError("El precio de un producto no puede ser negativo.")
        self._precio = float(valor)

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if int(valor) < 0:
            raise ValueError("El stock no puede ser negativo.")
        self._stock = int(valor)

    def tiene_stock(self, cantidad: int = 1) -> bool:
        """Verifica si hay stock suficiente para cubrir una cantidad solicitada."""
        return self._stock >= cantidad

    def descontar_stock(self, cantidad: int) -> None:
        """Descuenta unidades del stock validando disponibilidad."""
        if not self.tiene_stock(cantidad):
            raise ValueError(f"Stock insuficiente para {self.nombre}.")
        self._stock -= cantidad

    def valor_inventario(self) -> float:
        """Calcula el valor monetario total del stock de este producto."""
        return self._precio * self._stock

    def to_dict(self) -> dict:
        return {
            "ID": self.id_producto,
            "Nombre": self.nombre,
            "Marca": self.marca,
            "Modelo": self.modelo,
            "VRAM": self.vram,
            "Precio": self.precio,
            "Stock": self.stock,
            "Proveedor": self.proveedor_nombre,
        }

