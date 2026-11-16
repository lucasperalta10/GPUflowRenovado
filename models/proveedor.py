from typing import Optional
from models.base import EntidadBase


class Proveedor(EntidadBase):
    """
    Representa una empresa proveedora de placas de video.
    """

    def __init__(
        self,
        nombre: str,
        direccion: Optional[str] = None,
        email: Optional[str] = None,
        id_proveedor: Optional[int] = None,
    ):
        self.id_proveedor = id_proveedor
        self.nombre = nombre.strip() if nombre else ""
        self.direccion = direccion.strip() if direccion else None
        self.email = email.strip() if email else None

    def tiene_datos_validos(self) -> bool:
        """El nombre del proveedor es obligatorio."""
        return bool(self.nombre)

    def to_dict(self) -> dict:
        return {
            "id_proveedor": self.id_proveedor,
            "Nombre": self.nombre,
            "Direccion": self.direccion,
            "Correo_Electronico": self.email,
        }

