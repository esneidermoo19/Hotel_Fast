from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.errors import ConflictoError, NoEncontradoError
from app.core.pagination import PaginacionParams
from app.models import RolUsuario, Usuario
from app.schemas.usuario import (
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioPagina,
    UsuarioRead,
)
from app.services import auditoria_service, usuario_service

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])
solo_administradores = require_roles(RolUsuario.ADMIN)


@router.get(
    "",
    response_model=UsuarioPagina,
    summary="Listar usuarios",
    description="Lista usuarios con paginacion y filtros por rol, estado y texto.",
    responses={
        200: {"description": "Pagina de usuarios"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        422: {"description": "Parametros de consulta invalidos"},
    },
)
def listar_usuarios(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
    paginacion: Annotated[PaginacionParams, Depends()],
    rol: RolUsuario | None = None,
    activo: bool | None = None,
    q: str | None = None,
    solo_activos: Annotated[bool, Query(alias="soloActivos")] = False,
) -> UsuarioPagina:
    items, total = usuario_service.listar_usuarios(
        db,
        rol=rol,
        activo=activo,
        q=q,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
        solo_activos=solo_activos,
    )
    return UsuarioPagina(
        items=items,
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )


@router.get(
    "/{usuario_id}",
    response_model=UsuarioRead,
    summary="Obtener usuario",
    description="Obtiene un usuario por su identificador.",
    responses={
        200: {"description": "Usuario encontrado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Usuario no encontrado"},
    },
)
def obtener_usuario(
    usuario_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> UsuarioRead:
    try:
        return usuario_service.obtener_usuario(db, usuario_id)
    except usuario_service.UsuarioNoEncontradoError as error:
        raise NoEncontradoError(str(error)) from error


@router.post(
    "",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un usuario y registra la accion en la bitacora.",
    responses={
        201: {"description": "Usuario creado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        409: {"description": "El username o email ya existe"},
        422: {"description": "Datos de usuario invalidos"},
    },
)
def crear_usuario(
    request: Request,
    datos: UsuarioCrear,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> UsuarioRead:
    try:
        nuevo = usuario_service.crear_usuario(db, datos)
    except usuario_service.CredencialesDuplicadasError as error:
        raise ConflictoError(str(error)) from error
    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="CREAR_USUARIO",
        entidad="usuarios",
        entidad_id=nuevo.id,
        ip=request.client.host if request.client else None,
        detalle={"username": nuevo.username, "role": nuevo.role.value},
    )
    return nuevo


@router.put(
    "/{usuario_id}",
    response_model=UsuarioRead,
    summary="Actualizar usuario",
    description="Actualiza los datos de un usuario existente.",
    responses={
        200: {"description": "Usuario actualizado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "Los cambios entran en conflicto con las reglas de usuarios"},
        422: {"description": "Datos de usuario invalidos"},
    },
)
def actualizar_usuario(
    request: Request,
    usuario_id: int,
    datos: UsuarioActualizar,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> UsuarioRead:
    try:
        actualizado = usuario_service.actualizar_usuario(
            db,
            usuario_id,
            datos,
            usuario_actual=usuario,
        )
    except usuario_service.UsuarioNoEncontradoError as error:
        raise NoEncontradoError(str(error)) from error
    except usuario_service.CredencialesDuplicadasError as error:
        raise ConflictoError(str(error)) from error
    except usuario_service.UltimoAdministradorError as error:
        raise ConflictoError(str(error)) from error
    except usuario_service.NoSePuedeModificarASiMismoError as error:
        raise ConflictoError(str(error)) from error

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="ACTUALIZAR_USUARIO",
        entidad="usuarios",
        entidad_id=actualizado.id,
        ip=request.client.host if request.client else None,
        detalle=datos.model_dump(exclude_unset=True, exclude_none=True),
    )
    return actualizado


@router.post(
    "/{usuario_id}/desactivar",
    response_model=UsuarioRead,
    summary="Desactivar usuario",
    description="Desactiva una cuenta sin eliminar su historial.",
    responses={
        200: {"description": "Usuario desactivado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "No se puede desactivar esta cuenta"},
    },
)
def desactivar_usuario(
    request: Request,
    usuario_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> UsuarioRead:
    try:
        desactivado = usuario_service.desactivar_usuario(
            db,
            usuario_id,
            usuario_actual=usuario,
        )
    except usuario_service.UsuarioNoEncontradoError as error:
        raise NoEncontradoError(str(error)) from error
    except usuario_service.UltimoAdministradorError as error:
        raise ConflictoError(str(error)) from error
    except usuario_service.NoSePuedeModificarASiMismoError as error:
        raise ConflictoError(str(error)) from error

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="DESACTIVAR_USUARIO",
        entidad="usuarios",
        entidad_id=desactivado.id,
        ip=request.client.host if request.client else None,
    )
    return desactivado


@router.post(
    "/{usuario_id}/reactivar",
    response_model=UsuarioRead,
    summary="Reactivar usuario",
    description="Reactiva una cuenta de usuario desactivada.",
    responses={
        200: {"description": "Usuario reactivado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "Los cambios entran en conflicto con las reglas de usuarios"},
    },
)
def reactivar_usuario(
    request: Request,
    usuario_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> UsuarioRead:
    try:
        reactivado = usuario_service.actualizar_usuario(
            db,
            usuario_id,
            UsuarioActualizar(activo=True),
            usuario_actual=usuario,
        )
    except usuario_service.UsuarioNoEncontradoError as error:
        raise NoEncontradoError(str(error)) from error
    except usuario_service.CredencialesDuplicadasError as error:
        raise ConflictoError(str(error)) from error

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="REACTIVAR_USUARIO",
        entidad="usuarios",
        entidad_id=reactivado.id,
        ip=request.client.host if request.client else None,
    )
    return reactivado


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina fisicamente una cuenta creada por error.",
    responses={
        204: {"description": "Usuario eliminado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "No puedes eliminar tu propia cuenta"},
    },
)
def eliminar_usuario(
    usuario_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> Response:
    """Baja fisica. La API usa desactivar en el flujo normal; esto es para
    limpiar cuentas creadas por error."""
    try:
        objetivo = usuario_service.obtener_usuario(db, usuario_id)
    except usuario_service.UsuarioNoEncontradoError as error:
        raise NoEncontradoError(str(error)) from error
    if objetivo.id == usuario.id:
        raise ConflictoError("No puedes eliminar tu propia cuenta")
    db.delete(objetivo)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
