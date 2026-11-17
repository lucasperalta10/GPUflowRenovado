from dataclasses import dataclass, field
from typing import Optional
from src.models.base import EntidadBase


@dataclass(slots=True)
class Usuario(EntidadBase):
    """
    Representa un usuario autenticable en el sistema GPUflow.
    Oculta la contraseña/hash en la representación (__repr__) por seguridad.
    """

    username: str
    password: str = field(default="", repr=False)
    rol: str = "Admin"
    id_usuario: Optional[int] = None

    def __post_init__(self):
        self.username = self.username.strip() if self.username else ""

    def es_admin(self) -> bool:
        """Verifica si el usuario posee rol de administrador."""
        return (self.rol or "").lower() == "admin"

    def to_dict(self) -> dict:
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "rol": self.rol,
        }
