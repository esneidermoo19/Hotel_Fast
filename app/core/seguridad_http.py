"""Defensas HTTP transversales: cabeceras de seguridad y limite de cuerpo.

Se aplican a toda la API mediante middleware, para que ningun router tenga que
conocer detalles de infraestructura. Las cabeceras mitigan sniffing de tipos,
clickjacking, fugas de referer y abuso de APIs del navegador; HSTS solo se envia
en produccion (detras de HTTPS). El limite de cuerpo corta envios enormes antes
de que lleguen a los servicios.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.errors import CuerpoMuyGrandeError

CABECERAS_BASE: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Cross-Origin-Resource-Policy": "cross-origin",
}

HSTS_VALOR = "max-age=31536000; includeSubDomains"


def cabeceras_de_seguridad(*, produccion: bool) -> dict[str, str]:
    """Cabeceras a inyectar en cada respuesta segun el entorno."""
    cabeceras = dict(CABECERAS_BASE)
    if produccion:
        cabeceras["Strict-Transport-Security"] = HSTS_VALOR
    return cabeceras


def excede_limite_cuerpo(content_length: str | None, limite: int) -> bool:
    """Indica si el cuerpo anunciado supera el limite configurado.

    Un `Content-Length` ausente o invalido no se bloquea aqui (los clientes
    validos siempre lo envian); `limite <= 0` desactiva la comprobacion.
    """
    if limite <= 0 or content_length is None:
        return False
    try:
        return int(content_length) > limite
    except ValueError:
        return False


class CabecerasSeguridadMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        response = await call_next(request)
        for clave, valor in cabeceras_de_seguridad(
            produccion=settings.is_production
        ).items():
            response.headers.setdefault(clave, valor)
        return response


class LimiteCuerpoMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        if excede_limite_cuerpo(
            request.headers.get("content-length"),
            settings.max_request_body_bytes,
        ):
            error = CuerpoMuyGrandeError()
            return JSONResponse(
                status_code=error.status_code,
                content=error.to_payload(),
            )
        return await call_next(request)


def registrar_seguridad_http(app) -> None:  # type: ignore[no-untyped-def]
    """Conecta los middlewares de seguridad a la aplicacion FastAPI."""
    app.add_middleware(CabecerasSeguridadMiddleware)
    app.add_middleware(LimiteCuerpoMiddleware)
