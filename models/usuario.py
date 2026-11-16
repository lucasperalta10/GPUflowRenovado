from typing import Optional
from models.base import EntidadBase


class Usuario(EntidadBase):
    """
    Representa un usuario autenticable en el sistema GPUflow.
    """

    def __init__(
        self,
        username: str,
        password: str = "",
        rol: str = "Admin",
        id_usuario: Optional[int] = None,
    ):
        self.id_usuario = id_usuario
        self.username = username.strip() if username else ""
        self.password = password
        self.rol = rol

    def es_admin(self) -> bool:
        """Verifica si el usuario posee rol de administrador."""
        return self.rol.lower() == "admin"

    def to_dict(self) -> dict:
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "rol": self.rol,
        }

