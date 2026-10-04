"""Errores de dominio y sobre de error uniforme de la API.

Toda respuesta de error usa la forma:

    {"detail": "...", "code": "CODIGO", "errors": [...]}

`errors` solo se incluye cuando hay detalles por campo (validacion).
"""

from typing import Any

from fastapi import status


class AppError(Exception):
    """Error de dominio con codigo estable para el cliente."""

    codigo: str = "ERROR_INTERNO"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        detail: str,
        *,
        errors: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.errors = errors
        self.headers = headers

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"detail": self.detail, "code": self.codigo}
        if self.errors:
            payload["errors"] = self.errors
        return payload


class ValidacionError(AppError):
    codigo = "VALIDACION"
    status_code = 422


class NoAutorizadoError(AppError):
    codigo = "NO_AUTORIZADO"
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, detail: str = "Credenciales invalidas") -> None:
        super().__init__(detail, headers={"WWW-Authenticate": "Bearer"})


class TokenInvalidoError(NoAutorizadoError):
    codigo = "TOKEN_INVALIDO"

    def __init__(self, detail: str = "Token de acceso invalido") -> None:
        AppError.__init__(self, detail, headers={"WWW-Authenticate": "Bearer"})


class RefreshTokenInvalidoError(NoAutorizadoError):
    codigo = "REFRESH_TOKEN_INVALIDO"

    def __init__(self, detail: str = "Refresh token invalido") -> None:
        AppError.__init__(self, detail, headers={"WWW-Authenticate": "Bearer"})


class ProhibidoError(AppError):
    codigo = "SIN_PERMISOS"
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, detail: str = "No tienes permisos para esta accion") -> None:
        super().__init__(detail)


class NoEncontradoError(AppError):
    codigo = "NO_ENCONTRADO"
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, detail: str = "Recurso no encontrado") -> None:
        super().__init__(detail)


class ConflictoError(AppError):
    codigo = "CONFLICTO"
    status_code = status.HTTP_409_CONFLICT

    def __init__(
        self,
        detail: str = "La operacion entra en conflicto con el estado actual",
    ) -> None:
        super().__init__(detail)


class DemasiadasSolicitudesError(AppError):
    codigo = "DEMASIADAS_SOLICITUDES"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
