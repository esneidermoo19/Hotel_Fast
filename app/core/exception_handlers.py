"""Manejadores de excepciones que producen el sobre de error uniforme."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic.alias_generators import to_camel
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import AppError


def _campo_a_camel(segmento: Any) -> Any:
    if isinstance(segmento, str) and segmento.islower() and "_" in segmento:
        return to_camel(segmento)
    return segmento


def _detalles_validacion(exc: RequestValidationError) -> list[dict[str, Any]]:
    detalles: list[dict[str, Any]] = []
    for error in exc.errors():
        ubicacion = [_campo_a_camel(segmento) for segmento in error.get("loc", ())]
        # El primer segmento es la fuente del error (body, query, path...).
        campo = ".".join(str(segmento) for segmento in ubicacion[1:]) or None
        mensaje = error.get("msg", "Valor invalido")
        detalles.append(
            {
                "campo": campo,
                "mensaje": mensaje,
                "tipo": error.get("type", "invalid"),
            }
        )
    return detalles


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    def _app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_payload(),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    def _validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        detalles = _detalles_validacion(exc)
        primer_detalle = detalles[0]["mensaje"] if detalles else "Datos invalidos"
        return JSONResponse(
            status_code=422,
            content={
                "detail": f"Datos invalidos: {primer_detalle}",
                "code": "VALIDACION",
                "errors": detalles,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    def _database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Error de base de datos", "code": "BASE_DATOS"},
        )


class ErrorResponse(BaseModel):
    """Documenta el sobre de error en OpenAPI."""

    detail: str
    code: str
    errors: list[dict[str, Any]] | None = None
