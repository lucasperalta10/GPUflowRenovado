from typing import Optional
from sqlalchemy import select
from src.core.orm import UsuarioORM
from src.models.usuario import Usuario
from src.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    """
    Repositorio encargado de las operaciones sobre la tabla 'usuario' usando SQLAlchemy ORM.
    """

    def buscar_por_username(self, username: str) -> Optional[Usuario]:
        """Busca un usuario por su nombre de usuario y lo mapea a la entidad Usuario."""
        stmt = select(UsuarioORM).where(UsuarioORM.username == username.strip())
        row = self.session.scalar(stmt)
        if row is None:
            return None
        return Usuario(
            id_usuario=row.id_usuario,
            username=row.username,
            password=row.password,
            rol=row.rol or "Admin",
        )

    def crear_usuario(self, username: str, password_hash: str, rol: str = "Admin") -> Usuario:
        """Inserta un nuevo UsuarioORM en la sesión y retorna la entidad Usuario."""
        row = UsuarioORM(
            username=username.strip(),
            password=password_hash,
            rol=rol,
        )
        self.session.add(row)
        self.session.flush()
        return Usuario(
            id_usuario=row.id_usuario,
            username=row.username,
            password=row.password,
            rol=row.rol or "Admin",
        )

    def actualizar_password(self, id_usuario: int, password_hash: str) -> None:
        """Actualiza el hash de contraseña de un usuario existente."""
        row = self.session.get(UsuarioORM, id_usuario)
        if row:
            row.password = password_hash
            self.session.flush()
