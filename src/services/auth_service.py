from typing import Optional
from sqlalchemy.exc import IntegrityError
from src.core.database import get_session
from src.core.security import hash_password, verify_password
from src.models.usuario import Usuario
from src.repositories.usuario_repository import UsuarioRepository


class AuthService:
    """
    Servicio de autenticación y registro de usuarios.
    Contiene las reglas de negocio y validaciones de seguridad.
    """

    def login(self, username: str, password: str) -> tuple[Optional[Usuario], Optional[str]]:
        username = username.strip() if username else ""
        if not username or not password:
            return None, "Completemos usuario y contraseña."

        with get_session() as session:
            repo = UsuarioRepository(session)
            user = repo.buscar_por_username(username)

            if user is None:
                return None, "Las credenciales no son válidas."

            # Si el usuario ya tiene hash bcrypt, verificamos con bcrypt
            if user.password.startswith("$2"):
                if not verify_password(password, user.password):
                    return None, "Las credenciales no son válidas."
            else:
                # Compatibilidad con usuarios previos en texto plano (ej. admin/1234)
                if password != user.password:
                    return None, "Las credenciales no son válidas."
                # Si cumple longitud mínima, migramos automáticamente a hash bcrypt
                if 8 <= len(password) and len(password.encode("utf-8")) <= 72:
                    repo.actualizar_password(user.id_usuario, hash_password(password))

            return user, None

    def register(
        self, username: str, password: str, confirmation: str
    ) -> tuple[Optional[Usuario], Optional[str]]:
        username = username.strip() if username else ""

        if not (3 <= len(username) <= 50):
            return None, "El usuario debe tener entre 3 y 50 caracteres."
        if len(password) < 8 or len(password.encode("utf-8")) > 72:
            return None, "La contraseña debe tener al menos 8 caracteres y no superar 72 bytes."
        if password != confirmation:
            return None, "Las contraseñas no coinciden."

        try:
            password_hash = hash_password(password)
            with get_session() as session:
                repo = UsuarioRepository(session)
                if repo.buscar_por_username(username) is not None:
                    return None, "Ese nombre de usuario ya existe."
                user = repo.crear_usuario(username, password_hash, rol="Admin")
                return user, None
        except IntegrityError:
            return None, "Ese nombre de usuario ya existe."
