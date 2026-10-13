from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core import lockout
from app.core.errors import CuentaBloqueadaError
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
    if lockout.esta_bloqueado(identificador):
        raise CuentaBloqueadaError()
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
        lockout.registrar_intento_fallido(identificador)
        return None
    if not usuario.activo:
        return None
    lockout.limpiar_intentos(identificador)
    return usuario