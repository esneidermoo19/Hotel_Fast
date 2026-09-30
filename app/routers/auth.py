from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token
from app.models import Usuario
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.usuario import UsuarioRead
from app.services.auth_service import autenticar_usuario

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(usuario.id, usuario.role.value)
    return LoginResponse(
        token=token,
        id=usuario.id,
        username=usuario.username,
        email=usuario.email,
        nombre=usuario.nombre,
        role=usuario.role,
    )


@router.get("/me", response_model=UsuarioRead)
def obtener_sesion(
    usuario: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    return usuario


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion(
    usuario: Annotated[Usuario, Depends(get_current_user)],
) -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)