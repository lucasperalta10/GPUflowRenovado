from conexion import get_connection_pool
from src.services.auth_service import AuthService


def login_usuario(pool, username, password):
    user, _ = AuthService().login(username, password)
    return user.to_dict() if user else None


def crear_usuario(pool, username, password):
    user, _ = AuthService().register(username, password, password)
    return user is not None
