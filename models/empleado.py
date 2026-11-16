from typing import Optional
from models.base import Persona


class Empleado(Persona):
    """
    Representa un empleado del almacén.
    Hereda de Persona (nombre y apellido) y añade atributos propios del puesto.
    """

    def __init__(
        self,
        nombre: str,
        apellido: str,
        cargo: Optional[str] = None,
        id_empleado: Optional[int] = None,
        password: str = "",
    ):
        super().__init__(nombre, apellido)
        self.id_empleado = id_empleado
        self.cargo = cargo.strip() if cargo and cargo != "(Ninguno)" else None
        self.password = password

    def tiene_datos_validos(self) -> bool:
        """Valida que el empleado tenga nombre y apellido obligatorios."""
        return bool(self.nombre and self.apellido)

    def to_dict(self) -> dict:
        """Sobrescritura polimórfica de to_dict()."""
        return {
            "ID": self.id_empleado,
            "Nombre": self.nombre,
            "Apellido": self.apellido,
            "Cargo": self.cargo,
        }

