"""Tipos y parametros compartidos para listas paginadas."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query
from sqlalchemy import Select

from app.schemas.base import CamelCaseSchema

TAMANO_POR_DEFECTO = 20
TAMANO_MAXIMO = 100


@dataclass
class PaginacionParams:
    pagina: Annotated[int, Query(ge=1, description="Numero de pagina")] = 1
    tamano: Annotated[
        int,
        Query(ge=1, le=TAMANO_MAXIMO, description="Registros por pagina"),
    ] = TAMANO_POR_DEFECTO


class Pagina[T](CamelCaseSchema):
    items: list[T]
    total: int
    pagina: int
    tamano: int


def paginar_consulta[T](
    consulta: Select[tuple[T]],
    *,
    pagina: int,
    tamano: int,
) -> Select[tuple[T]]:
    return consulta.offset((pagina - 1) * tamano).limit(tamano)
