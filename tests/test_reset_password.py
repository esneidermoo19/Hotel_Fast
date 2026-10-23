import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import verify_password
from app.models import RolUsuario, Usuario
from app.reset_password import (
    buscar_usuario,
    main,
    restablecer_password,
    validar_password,
)
from tests.factories import crear_refresh_token, crear_usuario


@pytest.fixture
def sesion_cli(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> sessionmaker[Session]:
    fabrica = sessionmaker(bind=db_session.get_bind(), autoflush=False, autocommit=False)
    monkeypatch.setattr("app.reset_password.SessionLocal", fabrica)
    return fabrica


def _crear_admin(db: Session, **cambios: object) -> Usuario:
    datos: dict[str, object] = {
        "username": "adminhhf36",
        "email": "admin@example.com",
        "role": RolUsuario.ADMIN,
    }
    datos.update(cambios)
    return crear_usuario(db, **datos)  # type: ignore[arg-type]


def test_validar_password_exige_reglas() -> None:
    assert validar_password("Clave123") == []
    assert validar_password("corta1") != []
    assert validar_password("sinNumeros") != []
    assert validar_password("12345678") != []


def test_buscar_usuario_por_username_o_email(db_session: Session) -> None:
    usuario = _crear_admin(db_session, username="AdminX", email="AdminX@Example.com")

    assert buscar_usuario(db_session, "adminx") == usuario
    assert buscar_usuario(db_session, "  ADMINX@example.COM  ") == usuario
    assert buscar_usuario(db_session, "no-existe") is None


def test_restablecer_password_actualiza_hash_y_revoca_sesiones(
    db_session: Session,
) -> None:
    usuario = _crear_admin(db_session)
    token = crear_refresh_token(db_session, usuario=usuario)

    restablecer_password(db_session, usuario, "NuevaClave123")

    db_session.refresh(usuario)
    db_session.refresh(token)
    assert verify_password("NuevaClave123", usuario.password_hash)
    assert not verify_password("test-password-123", usuario.password_hash)
    assert token.revocado_en is not None


def test_restablecer_password_rechaza_password_debil(db_session: Session) -> None:
    usuario = _crear_admin(db_session)
    hash_original = usuario.password_hash

    with pytest.raises(ValueError):
        restablecer_password(db_session, usuario, "corta")

    db_session.refresh(usuario)
    assert usuario.password_hash == hash_original


def test_restablecer_password_puede_reactivar_la_cuenta(db_session: Session) -> None:
    usuario = _crear_admin(db_session, activo=False)

    restablecer_password(db_session, usuario, "NuevaClave123", activar=True)

    db_session.refresh(usuario)
    assert usuario.activo is True


def test_main_actualiza_la_contrasena(
    db_session: Session,
    sesion_cli: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    usuario = _crear_admin(db_session)
    monkeypatch.setattr("app.reset_password._pedir_password", lambda: "NuevaClave123")

    assert main(["--usuario", "adminhhf36"]) == 0

    db_session.refresh(usuario)
    assert verify_password("NuevaClave123", usuario.password_hash)


def test_main_devuelve_uno_si_el_usuario_no_existe(
    sesion_cli: sessionmaker[Session],
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--usuario", "no-existe"]) == 1
    assert "No se encontro el usuario" in capsys.readouterr().err


def test_main_rechaza_una_contrasena_invalida(
    db_session: Session,
    sesion_cli: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _crear_admin(db_session)
    monkeypatch.setattr("app.reset_password._pedir_password", lambda: "corta")

    assert main(["--usuario", "adminhhf36"]) == 1
