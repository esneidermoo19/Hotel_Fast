from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import RolUsuario, Usuario


class SeedSettings(BaseSettings):
    seed_admin_email: EmailStr
    seed_admin_username: str
    seed_admin_nombre: str
    seed_admin_password: str
    seed_recepcion_email: EmailStr
    seed_recepcion_username: str
    seed_recepcion_nombre: str
    seed_recepcion_password: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def _ensure_user(
    db: Session,
    *,
    email: str,
    username: str,
    nombre: str,
    password: str,
    role: RolUsuario,
) -> Usuario:
    normalized_email = email.casefold()
    normalized_username = username.casefold()
    existing_email = db.scalar(
        select(Usuario).where(func.lower(Usuario.email) == normalized_email)
    )
    existing_username = db.scalar(
        select(Usuario).where(func.lower(Usuario.username) == normalized_username)
    )
    if existing_email and existing_username and existing_email.id != existing_username.id:
        raise ValueError("El correo y el username del seed pertenecen a usuarios distintos")

    existing = existing_email or existing_username
    if existing is not None:
        if (
            existing.email.casefold() != normalized_email
            or existing.username.casefold() != normalized_username
            or existing.role != role
        ):
            raise ValueError("El usuario existente no coincide con la configuracion del seed")
        return existing

    usuario = Usuario(
        email=normalized_email,
        username=normalized_username,
        nombre=nombre,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(usuario)
    return usuario


def main() -> None:
    seed_settings = SeedSettings()
    db = SessionLocal()
    try:
        _ensure_user(
            db,
            email=str(seed_settings.seed_admin_email),
            username=seed_settings.seed_admin_username,
            nombre=seed_settings.seed_admin_nombre,
            password=seed_settings.seed_admin_password,
            role=RolUsuario.ADMIN,
        )
        _ensure_user(
            db,
            email=str(seed_settings.seed_recepcion_email),
            username=seed_settings.seed_recepcion_username,
            nombre=seed_settings.seed_recepcion_nombre,
            password=seed_settings.seed_recepcion_password,
            role=RolUsuario.RECEPCION,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()