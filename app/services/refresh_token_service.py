"""Emision, rotacion y revocacion de refresh tokens.

El token en claro se genera con `secrets` y solo viaja en la respuesta HTTP;
en la base de datos queda unicamente su hash SHA-256, de modo que una lectura
no autorizada de la tabla no permite suplantar a un usuario.
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import RefreshTokenInvalidoError
from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken
from app.models.usuario import Usuario

# Longitud en bytes del token aleatorio.
TOKEN_ENTROPY_BYTES = 32


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _a_utc(valor: datetime) -> datetime:
    """SQLite no conserva el tz; asumimos UTC al recuperar la columna."""
    return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor


def emitir_refresh_token(
    db: Session,
    usuario: Usuario,
    *,
    familia: str | None = None,
) -> str:
    """Crea un refresh token y devuelve su valor en claro."""
    token = secrets.token_urlsafe(TOKEN_ENTROPY_BYTES)
    db.add(
        RefreshToken(
            usuario_id=usuario.id,
            token_hash=hash_refresh_token(token),
            familia=familia or str(uuid.uuid4()),
            expira_en=_ahora() + timedelta(days=settings.refresh_token_expire_days),
        )
    )
    return token


def rotar_refresh_token(db: Session, token: str) -> tuple[Usuario, str]:
    """Valida un refresh token y lo reemplaza por uno nuevo de la misma familia.

    Presentar un token ya revocado se trata como robo de credenciales: se
    revoca la familia completa y la sesion muere.
    """
    registro = _buscar(db, token)
    if registro is None:
        raise RefreshTokenInvalidoError()

    momento = _ahora()
    if registro.revocado_en is not None:
        revocar_familia(db, registro.familia)
        db.commit()
        raise RefreshTokenInvalidoError(
            "Refresh token ya utilizado; se cierro la sesion"
        )

    if _a_utc(registro.expira_en) <= momento:
        raise RefreshTokenInvalidoError("Refresh token expirado")

    usuario = db.get(Usuario, registro.usuario_id)
    if usuario is None:
        raise RefreshTokenInvalidoError()

    nuevo_token = emitir_refresh_token(db, usuario, familia=registro.familia)
    registro.revocado_en = momento
    db.commit()
    return usuario, nuevo_token


def revocar_token(db: Session, token: str) -> None:
    """Revoca un refresh token concreto. Idempotente."""
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.token_hash == hash_refresh_token(token))
        .values(revocado_en=_ahora())
    )
    db.commit()


def revocar_familia(db: Session, familia: str) -> None:
    """Revoca todos los tokens vivos de una familia."""
    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.familia == familia,
            RefreshToken.revocado_en.is_(None),
        )
        .values(revocado_en=_ahora())
    )


def revocar_todos_del_usuario(db: Session, usuario_id: int) -> None:
    """Revoca todas las sesiones del usuario (cambio de clave o baja)."""
    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.usuario_id == usuario_id,
            RefreshToken.revocado_en.is_(None),
        )
        .values(revocado_en=_ahora())
    )
    db.commit()


def limpiar_vencidos(db: Session) -> int:
    """Borra tokens vencidos o revocados hace mas de 30 dias."""
    limite = _ahora() - timedelta(days=30)
    vencidos = db.scalars(
        select(RefreshToken).where(
            (RefreshToken.expira_en <= limite) | (RefreshToken.revocado_en <= limite)
        )
    ).all()
    for registro in vencidos:
        db.delete(registro)
    db.commit()
    return len(vencidos)


def _buscar(db: Session, token: str) -> RefreshToken | None:
    return db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(token))
    )
