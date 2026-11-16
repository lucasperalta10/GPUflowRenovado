from core.database import DatabaseConnection


class BaseRepository:
    """
    Clase base para todos los repositorios de acceso a datos.
    Centraliza el acceso al pool de conexiones (Herencia en capa de persistencia).
    """

    def __init__(self, pool=None):
        self.pool = pool if pool is not None else DatabaseConnection().get_pool()

    def _tiene_conexion(self) -> bool:
        return self.pool is not None

    def _obtener_conexion(self):
        if not self._tiene_conexion():
            raise ConnectionError("No hay pool de conexión disponible.")
        return self.pool.get_connection()

