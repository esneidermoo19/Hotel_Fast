"""Limitacion de intentos en los endpoints de autenticacion.

Bloquea ataques de fuerza bruta sobre login y refresh contando por IP,
usando el limite configurado en `LOGIN_RATE_LIMIT`.
"""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.errors import DemasiadasSolicitudesError

limiter = Limiter(key_func=get_remote_address)


def registrar_limiter(app) -> None:  # type: ignore[no-untyped-def]
    """Conecta slowapi a la app y traduce el 429 al sobre de error."""

    @app.exception_handler(RateLimitExceeded)
    def _demasiadas_solicitudes(
        request: Request,
        exc: RateLimitExceeded,
    ) -> JSONResponse:
        error = DemasiadasSolicitudesError(
            "Demasiados intentos; intenta de nuevo mas tarde"
        )
        return JSONResponse(
            status_code=error.status_code,
            content=error.to_payload(),
            headers={"Retry-After": "60"},
        )

    app.state.limiter = limiter
