from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.errors import NoAutorizadoError
from app.core.limiter import limiter
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


@router.post("/login", response_model=LoginResponse)
@limiter.limit(settings.login_rate_limit)
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


@router.post("/refresh", response_model=TokenPair)
@limiter.limit(settings.login_rate_limit)
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


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion(
    datos: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    refresh_token_service.revocar_token(db, datos.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/cambiar-password")
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
        direccion_ip=request.client.host if request.client else None,
    )
    return {"mensaje": "Contrasena actualizada"}


@router.get("/me", response_model=UsuarioRead)
def obtener_sesion(
    usuario: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    return usuario
