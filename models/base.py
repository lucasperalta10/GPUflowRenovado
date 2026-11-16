from abc import ABC, abstractmethod


class EntidadBase(ABC):
    """
    Clase abstracta base para todas las entidades del dominio.
    Aplica Abstracción y obliga a las subclases a implementar polimórficamente to_dict().
    """

    @abstractmethod
    def to_dict(self) -> dict:
        """Convierte la entidad en un diccionario serializable (Polimorfismo)."""
        pass


class Persona(EntidadBase):
    """
    Clase base que representa a una persona dentro del sistema.
    Sirve como superclase para aplicar Herencia (ej. Empleado).
    """

    def __init__(self, nombre: str, apellido: str):
        self.nombre = nombre.strip() if nombre else ""
        self.apellido = apellido.strip() if apellido else ""

    @property
    def nombre_completo(self) -> str:
        """Propiedad calculada que retorna 'Apellido, Nombre'."""
        return f"{self.apellido}, {self.nombre}"

    def to_dict(self) -> dict:
        return {
            "Nombre": self.nombre,
            "Apellido": self.apellido,
        }

