from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import HabitacionImagen
from app.seed import sembrar_imagenes
from tests.factories import crear_habitacion


@pytest.fixture
def media_dir(tmp_path, monkeypatch) -> Path:
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    return tmp_path


def _contar_imagenes(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(HabitacionImagen)) or 0


def test_siembra_imagenes_de_habitaciones_existentes(
    db_session: Session,
    media_dir: Path,
) -> None:
    crear_habitacion(db_session, numero=101)
    crear_habitacion(db_session, numero=201)

    creadas = sembrar_imagenes(db_session)

    assert creadas == 3
    assert _contar_imagenes(db_session) == 3
    assert (media_dir / "101-1.jpg").is_file()
    assert (media_dir / "201-1.jpg").is_file()
    assert (media_dir / "201-2.jpg").is_file()

    principales = db_session.scalars(
        select(HabitacionImagen).where(HabitacionImagen.es_principal.is_(True))
    ).all()
    assert len(principales) == 2


def test_siembra_es_idempotente(
    db_session: Session,
    media_dir: Path,
) -> None:
    crear_habitacion(db_session, numero=101)

    assert sembrar_imagenes(db_session) == 1
    assert sembrar_imagenes(db_session) == 0
    assert _contar_imagenes(db_session) == 1
    assert (media_dir / "101-1.jpg").is_file()


def test_no_toca_habitaciones_que_ya_tienen_imagenes(
    db_session: Session,
    media_dir: Path,
) -> None:
    habitacion = crear_habitacion(db_session, numero=101)
    db_session.add(
        HabitacionImagen(
            habitacion_id=habitacion.id,
            ruta="propia.jpg",
            orden=1,
            es_principal=True,
        )
    )
    db_session.commit()

    assert sembrar_imagenes(db_session) == 0

    imagenes = db_session.scalars(select(HabitacionImagen)).all()
    assert len(imagenes) == 1
    assert imagenes[0].ruta == "propia.jpg"


def test_repone_el_archivo_de_una_imagen_existente(
    db_session: Session,
    media_dir: Path,
) -> None:
    habitacion = crear_habitacion(db_session, numero=101)
    db_session.add(
        HabitacionImagen(
            habitacion_id=habitacion.id,
            ruta="101-1.jpg",
            orden=1,
            es_principal=True,
        )
    )
    db_session.commit()

    assert sembrar_imagenes(db_session) == 0
    assert (media_dir / "101-1.jpg").is_file()


def test_no_falla_si_no_hay_habitaciones(
    db_session: Session,
    media_dir: Path,
) -> None:
    assert sembrar_imagenes(db_session) == 0
    assert _contar_imagenes(db_session) == 0


def test_no_inserta_filas_si_falta_el_archivo(
    db_session: Session,
    media_dir: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    crear_habitacion(db_session, numero=101)
    assets_vacios = tmp_path / "assets"
    assets_vacios.mkdir()
    monkeypatch.setattr("app.seed.DIRECTORIO_IMAGENES", assets_vacios)

    assert sembrar_imagenes(db_session) == 0
    assert _contar_imagenes(db_session) == 0
