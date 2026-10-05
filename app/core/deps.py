from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import ProhibidoError, TokenInvalidoError
from app.models import RolUsuario, Usuario

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    unauthorized = TokenInvalidoError()
    if credentials is None:
        raise unauthorized
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = int(payload["sub"])
        role = payload["role"]
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise unauthorized from None

    user = db.get(Usuario, user_id)
    if user is None or user.role.value != role or not user.activo:
        raise unauthorized
    return user


def require_roles(*roles: RolUsuario) -> Callable[..., Usuario]:
    def role_dependency(
        current_user: Annotated[Usuario, Depends(get_current_user)],
    ) -> Usuario:
        if current_user.role not in roles:
            raise ProhibidoError("No tienes permisos para realizar esta accion")
        return current_user

    return role_dependency