from conexion import get_connection_pool
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository


def login_usuario(pool, username, password):
    repo = UsuarioRepository(pool)
    user = repo.autenticar(username, password)
    return user.to_dict() if user else None


def crear_usuario(pool, username, password):
    repo = UsuarioRepository(pool)
    nuevo = Usuario(username=username, password=password, rol="Admin")
    return repo.crear(nuevo)
