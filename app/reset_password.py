"""Restablece la contrasena de un usuario desde la linea de comandos.

Uso:
    python -m app.reset_password --usuario adminhhf36

La contrasena se solicita de forma interactiva y no se imprime. Al cambiarla se
revocan todas las sesiones del usuario.
"""

import argparse
import getpass
import sys
from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Usuario
from app.services.refresh_token_service import revocar_todos_del_usuario

LARGO_MINIMO = 8
LARGO_MAXIMO = 128


def validar_password(password: str) -> list[str]:
    errores: list[str] = []
    if len(password) < LARGO_MINIMO:
        errores.append(f"Debe tener al menos {LARGO_MINIMO} caracteres.")
    if len(password) > LARGO_MAXIMO:
        errores.append(f"Debe tener como maximo {LARGO_MAXIMO} caracteres.")
    if not any(caracter.isalpha() for caracter in password):
        errores.append("Debe incluir al menos una letra.")
    if not any(caracter.isdigit() for caracter in password):
        errores.append("Debe incluir al menos un numero.")
    return errores


def buscar_usuario(db: Session, identificador: str) -> Usuario | None:
    normalizado = identificador.strip().casefold()
    if not normalizado:
        return None
    return db.scalar(
        select(Usuario).where(
            or_(
                func.lower(Usuario.username) == normalizado,
                func.lower(Usuario.email) == normalizado,
            )
        )
    )


def restablecer_password(
    db: Session,
    usuario: Usuario,
    password: str,
    *,
    activar: bool = False,
) -> None:
    errores = validar_password(password)
    if errores:
        raise ValueError(" ".join(errores))

    usuario.password_hash = hash_password(password)
    if activar:
        usuario.activo = True
    revocar_todos_del_usuario(db, usuario.id)
    db.commit()


def _pedir_password() -> str:
    while True:
        password = getpass.getpass("Nueva contrasena: ")
        errores = validar_password(password)
        if errores:
            print(" ".join(errores), file=sys.stderr)
            continue
        confirmacion = getpass.getpass("Repite la nueva contrasena: ")
        if password != confirmacion:
            print("Las contrasenas no coinciden.", file=sys.stderr)
            continue
        return password


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Restablece la contrasena de un usuario de Hotel Fast."
    )
    parser.add_argument(
        "--usuario",
        required=True,
        help="Username o email del usuario a actualizar.",
    )
    parser.add_argument(
        "--activar",
        action="store_true",
        help="Reactiva la cuenta si esta inactiva.",
    )
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        usuario = buscar_usuario(db, args.usuario)
        if usuario is None:
            print("No se encontro el usuario indicado.", file=sys.stderr)
            return 1

        password = _pedir_password()
        restablecer_password(db, usuario, password, activar=args.activar)
        print(
            f"Contrasena actualizada para {usuario.username}. "
            "Se revocaron todas sus sesiones."
        )
        return 0
    except ValueError as error:
        db.rollback()
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        db.rollback()
        print(
            "No se pudo actualizar la contrasena. Verifica la conexion a la base de datos.",
            file=sys.stderr,
        )
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
