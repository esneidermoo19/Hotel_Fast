from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import Usuario


def autenticar_usuario(
    db: Session,
    username: str,
    email: str,
    password: str,
) -> Usuario | None:
    username_normalizado = username.casefold()
    email_normalizado = email.casefold()
    usuario = db.scalar(
        select(Usuario).where(
            or_(
                func.lower(Usuario.username) == username_normalizado,
                func.lower(Usuario.email) == email_normalizado,
            )
        )
    )
    if usuario is None or not verify_password(password, usuario.password_hash):
        return None
    return usuario