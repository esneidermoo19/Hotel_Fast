"""Pruebas para app.dev_db."""

from sqlalchemy import inspect


def test_dev_db_rejects_postgres(monkeypatch):
    """Debe negarse a correr con URL de PostgreSQL."""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@host/db")

    # Recargar settings
    import importlib
    import app.core.config as config_module

    importlib.reload(config_module)
    from app.core.config import settings

    assert settings.environment == "development"
    assert settings.database_url.startswith("postgresql")

    # Ejecutar dev_db.main y esperar salida 1
    from app.dev_db import main

    assert main() == 1


def test_dev_db_creates_tables_with_sqlite(monkeypatch):
    """Debe crear tablas usuarios y habitaciones con SQLite en memoria."""
    # Usar SQLite en memoria para la prueba
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    import importlib
    import app.core.config as config_module

    importlib.reload(config_module)
    from app.core.config import settings

    assert settings.environment == "development"
    assert settings.database_url == "sqlite:///:memory:"

    from app.core.database import Base, engine
    import app.models  # noqa: F401

    # Crear tablas
    Base.metadata.create_all(bind=engine)

    # Verificar que existen las tablas
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "usuarios" in tables
    assert "habitaciones" in tables

    # Verificar columnas clave
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