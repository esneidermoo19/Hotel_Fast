from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.errors import NoEncontradoError
from app.models import Usuario
from app.schemas.catalogo import CatalogoRead
from app.services import catalogos_service

router = APIRouter(prefix="/api/catalogos", tags=["catalogos"])


@router.get(
    "",
    response_model=list[CatalogoRead],
    summary="Listar catalogos",
    description="Lista los catalogos disponibles para la aplicacion.",
    responses={
        200: {"description": "Listado de catalogos"},
        401: {"description": "Token de acceso invalido o ausente"},
    },
)
def listar_catalogos(
    usuario: Annotated[Usuario, Depends(get_current_user)],
) -> list[CatalogoRead]:
    return catalogos_service.listar_catalogos()


@router.get(
    "/{nombre}",
    response_model=CatalogoRead,
    summary="Obtener catalogo",
    description="Obtiene las opciones de un catalogo por su nombre.",
    responses={
        200: {"description": "Catalogo encontrado"},
        401: {"description": "Token de acceso invalido o ausente"},
        404: {"description": "Catalogo no encontrado"},
    },
)
def obtener_catalogo(
    nombre: str,
    usuario: Annotated[Usuario, Depends(get_current_user)],
) -> CatalogoRead:
    catalogo = catalogos_service.obtener_catalogo(nombre)
    if catalogo is None:
        raise NoEncontradoError(f"No existe el catalogo {nombre}")
    return catalogo
