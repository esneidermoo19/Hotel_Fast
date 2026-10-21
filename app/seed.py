import logging
import shutil
from pathlib import Path

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Habitacion, HabitacionImagen, RolUsuario, Usuario

logger = logging.getLogger(__name__)

DIRECTORIO_IMAGENES = Path(__file__).resolve().parent / "seed_assets" / "imagenes"

MAPEO_IMAGENES: dict[int, tuple[str, ...]] = {
    101: ("101-1.jpg",),
    102: ("102-1.jpg",),
    201: ("201-1.jpg", "201-2.jpg"),
    202: ("202-1.jpg", "202-2.jpg"),
    301: ("301-1.jpg",),
    302: ("302-1.jpg",),
    401: ("401-1.jpg",),
    402: ("402-1.jpg",),
}


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


def _copiar_si_falta(directorio_media: Path, nombre: str) -> bool:
    origen = DIRECTORIO_IMAGENES / nombre
    if not origen.is_file():
        logger.warning("No existe la imagen de seed %s", origen)
        return False

    destino = directorio_media / nombre
    if not destino.exists():
        shutil.copy2(origen, destino)
    return True


def sembrar_imagenes(db: Session) -> int:
    """Copia las imagenes de ejemplo y crea sus registros.

    Solo actua sobre habitaciones existentes que aun no tienen imagenes. Si una
    habitacion ya tiene filas, solo repone los archivos que falten. Devuelve
    cuantas imagenes se crearon.
    """
    if not DIRECTORIO_IMAGENES.is_dir():
        return 0

    directorio_media = Path(settings.media_dir)
    directorio_media.mkdir(parents=True, exist_ok=True)
    creadas = 0

    try:
        for numero, nombres in MAPEO_IMAGENES.items():
            habitacion = db.scalar(
                select(Habitacion).where(Habitacion.numero == numero)
            )
            if habitacion is None:
                continue

            existentes = db.scalars(
                select(HabitacionImagen).where(
                    HabitacionImagen.habitacion_id == habitacion.id
                )
            ).all()
            if existentes:
                for imagen in existentes:
                    _copiar_si_falta(directorio_media, imagen.ruta)
                continue

            for orden, nombre in enumerate(nombres, start=1):
                if not _copiar_si_falta(directorio_media, nombre):
                    continue
                db.add(
                    HabitacionImagen(
                        habitacion_id=habitacion.id,
                        ruta=nombre,
                        orden=orden,
                        es_principal=orden == 1,
                    )
                )
                creadas += 1

        db.commit()
    except Exception:
        db.rollback()
        raise

    return creadas


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
        imagenes = sembrar_imagenes(db)
        if imagenes:
            print(f"Imagenes de ejemplo sembradas: {imagenes}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
