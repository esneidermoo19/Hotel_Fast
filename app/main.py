from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.routing import APIRoute
from pydantic.alias_generators import to_camel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exception_handlers import registrar_manejadores
from app.core.limiter import registrar_limiter
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


app = FastAPI(
    title="Hotel Fast - API de gestion hotelera",
    description="API para la administracion integral de las operaciones del hotel.",
    version="1.0.0",
    openapi_url=None if settings.is_production else "/openapi.json",
    docs_url=None,
    redoc_url=None if settings.is_production else "/redoc",
    openapi_tags=openapi_tags,
    swagger_ui_parameters={"persistAuthorization": True},
    generate_unique_id_function=generar_operation_id,
    responses={
        422: {
            "description": "Solicitud invalida por datos o parametros incorrectos",
        }
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
registrar_limiter(app)
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


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


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