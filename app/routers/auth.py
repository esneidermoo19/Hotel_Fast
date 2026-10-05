from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.errors import NoAutorizadoError
from app.core.limiter import limite_login, limiter
from app.core.security import create_access_token
from app.models import Usuario
from app.schemas.auth import (
    CambiarPasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    TokenPair,
)
from app.schemas.usuario import UsuarioRead
from app.services import auditoria_service, refresh_token_service, usuario_service
from app.services.auth_service import autenticar_usuario

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Iniciar sesion",
    description="Valida un username o email y devuelve tokens de acceso.",
    responses={
        200: {"description": "Sesion iniciada"},
        401: {"description": "Credenciales incorrectas"},
        422: {"description": "Solicitud invalida"},
    },
)
@limiter.limit(limite_login())
def login(
    request: Request,
    datos: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    usuario = autenticar_usuario(
        db,
        username=datos.username,
        email=datos.email,
        password=datos.password,
    )
    if usuario is None:
        raise NoAutorizadoError("Credenciales incorrectas")
    refresh_token = refresh_token_service.emitir_refresh_token(db, usuario)
    db.commit()
    return LoginResponse(
        token=create_access_token(usuario.id, usuario.role.value),
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        id=usuario.id,
        username=usuario.username,
        email=usuario.email,
        nombre=usuario.nombre,
        role=usuario.role,
    )


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Renovar tokens",
    description="Rota el refresh token y emite un nuevo par de tokens.",
    responses={
        200: {"description": "Tokens renovados"},
        401: {"description": "Refresh token invalido"},
    },
)
@limiter.limit(limite_login())
def refrescar_token(
    request: Request,
    datos: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenPair:
    usuario, refresh_token = refresh_token_service.rotar_refresh_token(
        db,
        datos.refresh_token,
    )
    return TokenPair(
        token=create_access_token(usuario.id, usuario.role.value),
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesion",
    description="Revoca el refresh token proporcionado.",
    responses={
        204: {"description": "Sesion cerrada"},
        401: {"description": "Refresh token invalido"},
    },
)
def cerrar_sesion(
    datos: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    refresh_token_service.revocar_token(db, datos.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/cambiar-password",
    summary="Cambiar contrasena",
    description="Actualiza la contrasena del usuario autenticado.",
    responses={
        200: {"description": "Contrasena actualizada"},
        401: {"description": "Token de acceso invalido o ausente"},
        422: {"description": "Solicitud invalida"},
    },
)
def cambiar_password(
    request: Request,
    datos: CambiarPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(get_current_user)],
) -> dict[str, str]:
    """Cambia la contraseña propia y cierra el resto de sesiones abiertas."""
    usuario_service.cambiar_password(
        db,
        usuario,
        password_actual=datos.password_actual,
        password_nuevo=datos.password_nuevo,
    )
    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="CAMBIAR_PASSWORD",
        entidad="usuarios",
        entidad_id=usuario.id,
        ip=request.client.host if request.client else None,
    )
    return {"mensaje": "Contrasena actualizada"}


@router.get(
    "/me",
    response_model=UsuarioRead,
    summary="Obtener sesion actual",
    description="Devuelve los datos del usuario autenticado.",
    responses={
        200: {"description": "Sesion actual"},
        401: {"description": "Token de acceso invalido o ausente"},
    },
)
def obtener_sesion(
    usuario: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    return usuario
