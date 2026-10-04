#!/usr/bin/env python3
"""Inicializa la base de datos de desarrollo (SQLite).

Uso: python -m app.dev_db
"""

import sys

import app.models  # noqa: F401 - registra modelos
from app.core.config import settings
from app.core.database import Base, engine


def main() -> int:
    if settings.environment.strip().lower() != "development":
        print("ERROR: Solo se permite ejecutar en environment=development", file=sys.stderr)
        return 1

    db_url = settings.database_url or ""
    if not db_url.startswith("sqlite"):
        print(
            f"ERROR: DATABASE_URL debe ser SQLite (actual: {db_url})",
            file=sys.stderr,
        )
        return 1

    Base.metadata.create_all(bind=engine)
    print(f"Base de datos inicializada: {db_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())