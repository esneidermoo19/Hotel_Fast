"""Reglas de negocio de usuarios.

Restricciones que el router solo traduce a HTTP:
- username y email son únicos, sin distinguir mayúsculas
- la contraseña debe cumplir la regla de fortaleza
- no se puede desactivar ni degradar al último administrador activo
- desactivar o cambiar la contraseña revoca todas las sesiones del usuario
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError, ValidacionError
from app.core.passwords import mensaje_de_fortaleza
from app.core.security import hash_password, verify_password
from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import UsuarioActualizar, UsuarioCrear
from app.services import refresh_token_service


class UsuarioNoEncontradoError(LookupError):
    def __init__(self) -> None:
        super().__init__("No se encontro el usuario")


class CredencialesDuplicadasError(ValueError):
    def __init__(self, campo: str, valor: str) -> None:
        super().__init__(f"Ya existe un usuario con {campo} {valor}")


class UltimoAdministradorError(ValueError):
    def __init__(self) -> None:
        super().__init__("No se puede desactivar ni degradar al ultimo administrador")


class NoSePuedeModificarASiMismoError(ValueError):
    def __init__(self, accion: str) -> None:
        super().__init__(f"No puedes {accion} tu propia cuenta desde esta pantalla")


def listar_usuarios(db: Session, *, solo_activos: bool = False) -> list[Usuario]:
    consulta = select(Usuario).order_by(Usuario.id)
    if solo_activos:
        consulta = consulta.where(Usuario.activo.is_(True))
    return list(db.scalars(consulta).all())


def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError
    return usuario


def crear_usuario(db: Session, datos: UsuarioCrear) -> Usuario:
    _verificar_unicidad(db, username=datos.username, email=datos.email)
    _exigir_password_valido(datos.password)
    usuario = Usuario(
        username=datos.username.casefold(),
        email=str(datos.email).casefold(),
        nombre=datos.nombre,
        password_hash=hash_password(datos.password),
        role=datos.role,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar_usuario(
    db: Session,
    usuario_id: int,
    datos: UsuarioActualizar,
    *,
    usuario_actual: Usuario,
) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)

    username = datos.username.casefold() if datos.username is not None else None
    email = str(datos.email).casefold() if datos.email is not None else None
    _verificar_unicidad(
        db,
        username=username,
        email=email,
        excluir_id=usuario_id,
    )

    degrada_admin = (
        usuario.role == RolUsuario.ADMIN
        and datos.role is not None
        and datos.role != RolUsuario.ADMIN
    )
    if degrada_admin and _contar_administradores_activos(db) <= 1:
        raise UltimoAdministradorError

    if datos.username is not None:
        usuario.username = username or usuario.username
    if datos.email is not None:
        usuario.email = email or usuario.email
    if datos.nombre is not None:
        usuario.nombre = datos.nombre
    if datos.role is not None:
        usuario.role = datos.role
    if datos.activo is not None:
        _cambiar_activo(db, usuario, datos.activo, usuario_actual=usuario_actual)

    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_password(
    db: Session,
    usuario: Usuario,
    *,
    password_actual: str,
    password_nuevo: str,
) -> None:
    """Cambia la contraseña del propio usuario y cierra sus otras sesiones."""
    if not verify_password(password_actual, usuario.password_hash):
        raise ConflictoError("La contraseña actual no es correcta")
    _exigir_password_valido(password_nuevo)
    if verify_password(password_nuevo, usuario.password_hash):
        raise ValidacionError("La contraseña nueva debe ser distinta de la actual")
    usuario.password_hash = hash_password(password_nuevo)
    db.commit()
    refresh_token_service.revocar_todos_del_usuario(db, usuario.id)


def desactivar_usuario(
    db: Session,
    usuario_id: int,
    *,
    usuario_actual: Usuario,
) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)
    _cambiar_activo(db, usuario, False, usuario_actual=usuario_actual)
    db.commit()
    db.refresh(usuario)
    return usuario


def _cambiar_activo(
    db: Session,
    usuario: Usuario,
    activo: bool,
    *,
    usuario_actual: Usuario,
) -> None:
    # El guard de ultimo administrador va primero: si solo hay un admin y
    # trata de desactivarse, ese es el motivo real que debe reportarse.
    if (
        not activo
        and usuario.role == RolUsuario.ADMIN
        and _contar_administradores_activos(db) <= 1
    ):
        raise UltimoAdministradorError
    if usuario.id == usuario_actual.id and not activo:
        raise NoSePuedeModificarASiMismoError("desactivar")
    usuario.activo = activo
    if not activo:
        refresh_token_service.revocar_todos_del_usuario(db, usuario.id)


def _contar_administradores_activos(db: Session) -> int:
    return db.scalar(
        select(func.count(Usuario.id)).where(
            Usuario.role == RolUsuario.ADMIN,
            Usuario.activo.is_(True),
        )
    ) or 0


def _verificar_unicidad(
    db: Session,
    *,
    username: str | None,
    email: str | None,
    excluir_id: int | None = None,
) -> None:
    if username:
        consulta = select(Usuario.id).where(
            func.lower(Usuario.username) == username.casefold()
        )
        if excluir_id is not None:
            consulta = consulta.where(Usuario.id != excluir_id)
        if db.scalar(consulta) is not None:
            raise CredencialesDuplicadasError("username", username)

    if email:
        consulta = select(Usuario.id).where(func.lower(Usuario.email) == email.casefold())
        if excluir_id is not None:
            consulta = consulta.where(Usuario.id != excluir_id)
        if db.scalar(consulta) is not None:
            raise CredencialesDuplicadasError("email", email)


def _exigir_password_valido(password: str) -> None:
    problema = mensaje_de_fortaleza(password)
    if problema:
        raise ValidacionError(problema)
