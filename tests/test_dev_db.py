"""Pruebas para app.dev_db."""

import importlib

from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

import app.core.config as config_module
import app.models  # noqa: F401


def _reload_modules():
    importlib.reload(config_module)
    import app.dev_db as dev_db_module
    importlib.reload(dev_db_module)
    from app.core.config import settings as reloaded_settings
    from app.dev_db import main as reloaded_main
    return reloaded_settings, reloaded_main


def test_dev_db_rejects_postgres(monkeypatch):
    """Debe negarse a correr con URL de PostgreSQL."""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@host/db")

    settings, main = _reload_modules()

    assert settings.environment == "development"
    assert settings.database_url.startswith("postgresql")

    assert main() == 1


def test_dev_db_creates_tables_with_sqlite(monkeypatch):
    """Debe crear tablas usuarios y habitaciones con SQLite en memoria."""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    settings, main = _reload_modules()

    assert settings.environment == "development"
    assert settings.database_url == "sqlite:///:memory:"

    # Engine local con la URL del monkeypatch, sin depender del .env
    local_engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    from app.core.database import Base
    Base.metadata.create_all(bind=local_engine)

    inspector = inspect(local_engine)
    tables = inspector.get_table_names()
    assert "usuarios" in tables
    assert "habitaciones" in tables

    usuarios_cols = {c["name"] for c in inspector.get_columns("usuarios")}
    assert {"id", "username", "email", "nombre", "password_hash", "role"}.issubset(
        usuarios_cols
    )

    habitaciones_cols = {c["name"] for c in inspector.get_columns("habitaciones")}
    assert {
        "id",
        "numero",
        "tipo",
        "capacidad",
        "precio_por_noche",
        "estado",
    }.issubset(habitaciones_cols)