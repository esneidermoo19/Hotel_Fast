import os
from os import PathLike
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from pydantic.alias_generators import to_camel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.types import Scope

from app.core.config import Settings, settings
from app.core.database import get_db
from app.core.exception_handlers import registrar_manejadores
from app.core.limiter import registrar_limiter
from app.core.seguridad_http import registrar_seguridad_http
from app.routers import (
    auditoria,
    auth,
    catalogos,
    consumos,
    cuentas,
    dashboard,
    habitaciones,
    horarios,
    huespedes,
    pagos,
    reportes,
    reservas,
    usuarios,
)

openapi_tags = [
    {"name": "auth", "description": "Autenticacion y gestion de sesiones."},
    {"name": "habitaciones", "description": "Gestion de habitaciones del hotel."},
    {"name": "huespedes", "description": "Gestion de huespedes y sus reservas."},
    {"name": "usuarios", "description": "Administracion de usuarios y permisos."},
    {"name": "catalogos", "description": "Consulta de catalogos del sistema."},
    {"name": "auditoria", "description": "Consulta de eventos de auditoria."},
    {"name": "reservas", "description": "Gestion de reservas hoteleras."},
    {"name": "pagos", "description": "Gestion de pagos y transacciones."},
    {"name": "consumos", "description": "Gestion de consumos asociados a reservas."},
    {"name": "cuentas", "description": "Gestion de cuentas y cargos de huespedes."},
    {"name": "horarios", "description": "Gestion de horarios del personal."},
    {"name": "reportes", "description": "Consulta de reportes operativos."},
    {"name": "dashboard", "description": "Indicadores generales del hotel."},
    {"name": "health", "description": "Estado del servicio y sus dependencias."},
]


def generar_operation_id(route: APIRoute) -> str:
    return to_camel(route.name)


def documentacion_habilitada(config: Settings = settings) -> bool:
    """Publica Swagger, ReDoc y OpenAPI en produccion solo con DOCS_ENABLED=true."""
    return not config.is_production or config.docs_enabled


DOCUMENTACION_HABILITADA = documentacion_habilitada()


app = FastAPI(
    title="Hotel Fast - API de gestion hotelera",
    description="API para la administracion integral de las operaciones del hotel.",
    version="1.0.0",
    openapi_url="/openapi.json" if DOCUMENTACION_HABILITADA else None,
    docs_url=None,
    redoc_url="/redoc" if DOCUMENTACION_HABILITADA else None,
    openapi_tags=openapi_tags,
    swagger_ui_parameters={"persistAuthorization": True},
    generate_unique_id_function=generar_operation_id,
    responses={
        422: {
            "description": "Solicitud invalida por datos o parametros incorrectos",
        }
    },
)
# El orden importa: CORS se agrega AL FINAL para quedar como middleware mas
# externo entre los de la app, de modo que tambien cubra las respuestas que
# generan los demas middlewares (413 de tamano y 429 de limite global).
registrar_limiter(app)
registrar_seguridad_http(app)
# Comprime las respuestas (JSON) para acelerar la carga en el cliente.
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.resolved_cors_origin_regex,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type"],
    expose_headers=["Retry-After", "WWW-Authenticate"],
)
registrar_manejadores(app)
app.include_router(auth.router)
app.include_router(habitaciones.router)
app.include_router(huespedes.router)
app.include_router(usuarios.router)
app.include_router(catalogos.router)
app.include_router(auditoria.router)
app.include_router(reservas.router)
app.include_router(pagos.router)
app.include_router(consumos.router)
app.include_router(cuentas.router)
app.include_router(horarios.router)
app.include_router(reportes.router)
app.include_router(dashboard.router)
class _MediaEstatica(StaticFiles):
    """Sirve /media con cache larga.

    Los archivos tienen nombre unico e inmutable, asi que el navegador puede
    cachearlos por mucho tiempo sin revalidar (fluidez al reabrir).
    """

    def file_response(
        self,
        full_path: str | PathLike[str],
        stat_result: os.stat_result,
        scope: Scope,
        status_code: int = 200,
    ) -> Response:
        response = super().file_response(full_path, stat_result, scope, status_code)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


app.mount(
    settings.media_url_prefix,
    _MediaEstatica(directory=settings.media_dir, check_dir=False),
    name="media",
)


def _montar_documentacion() -> None:
    """Expone Swagger UI fuera de produccion o con DOCS_ENABLED=true.

    En produccion la API no publica ni el esquema OpenAPI ni la UI por defecto,
    para no revelar la superficie de endpoints a un atacante.
    """
    if not DOCUMENTACION_HABILITADA:
        return

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title=f"{app.title} - Swagger UI",
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )


_montar_documentacion()


@app.get(
    "/",
    response_model=None,
    tags=["health"],
    summary="Consultar informacion del servicio",
    description=(
        "Devuelve el nombre, la version y las rutas utiles para consumir la API."
    ),
    responses={200: {"description": "Informacion del servicio"}},
)
def info_servicio() -> dict[str, str | None]:
    return {
        "nombre": app.title,
        "version": app.version,
        "estado": "ok",
        "salud": "/api/health",
        "documentacion": "/docs" if DOCUMENTACION_HABILITADA else None,
    }


@app.get(
    "/api/health",
    response_model=None,
    tags=["health"],
    summary="Comprobar estado del servicio",
    description="Verifica que la API y la base de datos esten disponibles.",
    responses={
        200: {"description": "Servicio disponible"},
        503: {"description": "Base de datos no disponible"},
    },
)
def health_check(
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str] | JSONResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Base de datos no disponible",
                "code": "NO_DISPONIBLE",
            },
        )
    return {"status": "ok"}