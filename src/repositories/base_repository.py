from sqlalchemy.orm import Session


class BaseRepository:
    """
    Clase base para todos los repositorios de acceso a datos con SQLAlchemy.
    Recibe una Session activa por inyección de dependencias.
    """

    def __init__(self, session: Session):
        self.session = session
