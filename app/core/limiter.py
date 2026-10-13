"""Limitacion de intentos en los endpoints de autenticacion.

Bloquea ataques de fuerza bruta sobre login y refresh contando por IP.
El limite sale de la configuracion (`LOGIN_RATE_LIMIT_PER_MINUTE`) y puede
desactivarse por completo con `RATE_LIMIT_ENABLED`.
"""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.errors import DemasiadasSolicitudesError

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.global_rate_limit_per_minute}/minute"],
)


def limite_login() -> str:
    """Expresion de slowapi construida desde la configuracion."""
    return f"{settings.login_rate_limit_per_minute}/minute"


def registrar_limiter(app) -> None:  # type: ignore[no-untyped-def]
    """Conecta slowapi a la app y traduce el 429 al sobre de error."""

    @app.exception_handler(RateLimitExceeded)
    def _limite_excedido(
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

    limiter.enabled = settings.rate_limit_enabled
    app.state.limiter = limiter
    # Aplica el limite global por IP a las rutas sin decorador propio.
    app.add_middleware(SlowAPIMiddleware)
