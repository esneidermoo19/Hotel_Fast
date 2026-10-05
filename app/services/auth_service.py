from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import Usuario

_HASH_FALSO = hash_password("verificacion-de-credenciales-falsas")


def autenticar_usuario(
    db: Session,
    username: str | None,
    email: str | None,
    password: str,
) -> Usuario | None:
    identificador = (username or email or "").casefold()
    encontrados = list(
        db.scalars(
            select(Usuario).where(
                or_(
                    func.lower(Usuario.username) == identificador,
                    func.lower(Usuario.email) == identificador,
                )
            )
        ).all()
    )
    usuario = encontrados[0] if len(encontrados) == 1 else None
    hash_almacenado = usuario.password_hash if usuario is not None else _HASH_FALSO
    password_correcta = verify_password(password, hash_almacenado)
    if usuario is None or not password_correcta:
        return None
    if not usuario.activo:
        return None
    return usuario