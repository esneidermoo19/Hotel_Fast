"""Paginación por offset/limit.

Se usa como dependencia para no repetir los mismos `Query` en cada router.
"""

from typing import Annotated

from fastapi import Query

from app.schemas.base import CamelCaseSchema

LIMITE_POR_DEFECTO = 50
LIMITE_MAXIMO = 200


class Paginacion(CamelCaseSchema):
    limite: int
    offset: int
    total: int

    @property
    def siguiente_offset(self) -> int | None:
        siguiente = self.offset + self.limite
        return siguiente if siguiente < self.total else None


def parametros_paginacion(
    limite: Annotated[
        int,
        Query(ge=1, le=LIMITE_MAXIMO, description="Maximo de registros por pagina"),
    ] = LIMITE_POR_DEFECTO,
    offset: Annotated[int, Query(ge=0, description="Registros a omitir")] = 0,
) -> tuple[int, int]:
    return limite, offset
