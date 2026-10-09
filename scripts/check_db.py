"""Verifica la conexion a la base de datos antes de `alembic upgrade head`.

Lee DATABASE_URL del entorno o del archivo .env (sin imprimir la contrasena),
aplica el mismo percent-encoding que app/core/config.py y prueba la conexion.

Uso:
    python scripts/check_db.py
"""
import os
import sys
from pathlib import Path
from urllib.parse import quote, unquote


def _cargar_dotenv() -> None:
    ruta = Path(__file__).resolve().parent.parent / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        clave = clave.strip()
        valor = valor.strip().strip('"').strip("'")
        if clave and clave not in os.environ:
            os.environ[clave] = valor


def codificar_contrasena(url: str) -> str:
    """Percent-encoding de la contrasena, replicando app/core/config.py."""
    scheme, sep, resto = url.partition("://")
    if not sep:
        return url
    userinfo, at, endpoint = resto.rpartition("@")
    if not at or ":" not in userinfo:
        return url
    usuario, clave = userinfo.split(":", 1)
    clave = quote(unquote(clave), safe="")
    host, slash, path = endpoint.partition("/")
    base = f"{scheme}://{usuario}:{clave}@{host}"
    return f"{base}/{path}" if slash else base


def main() -> int:
    _cargar_dotenv()
    raw = os.environ.get("DATABASE_URL")
    if not raw:
        print("No se encontro DATABASE_URL (ni en el entorno ni en .env).", file=sys.stderr)
        return 2

    url = codificar_contrasena(raw)

    # Mostrar solo host/base/usuario; nunca la contrasena.
    from sqlalchemy.engine import make_url

    destino = make_url(url)
    print(f"Probando conexion como {destino.username} a "
          f"{destino.host}:{destino.port or 5432}/{destino.database} ...")

    from sqlalchemy import create_engine, text

    # Timeout corto para Postgres; evita quedarse colgado ante un host filtrado.
    connect_args = {"connect_timeout": 10} if url.startswith("postgres") else {}

    try:
        engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)
        with engine.connect() as conexion:
            base, usuario = conexion.execute(
                text("SELECT current_database(), current_user")
            ).one()
        print(f"CONEXION OK: base={base}, usuario={usuario}")
        return 0
    except Exception as error:  # noqa: BLE001
        print(f"FALLO: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
