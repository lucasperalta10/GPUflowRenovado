import bcrypt


def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt con sal aleatoria.
    Exige mínimo 8 caracteres y máximo 72 bytes (límite de bcrypt).
    """
    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        raise ValueError("La contraseña debe tener entre 8 caracteres y 72 bytes.")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica una contraseña en texto plano contra su hash bcrypt almacenado.
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
