from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    habitaciones,
    huespedes,
    usuarios,
)

app = FastAPI(title=settings.app_name)
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


@app.get("/api/health", response_model=None, tags=["health"])
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