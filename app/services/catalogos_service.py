"""Catálogos de valores permitidos.

El frontend los consume para poblar desplegables sin duplicar en su lado la
lista de valores que el backend admite. Los enums vienen de
`app.models.enums`, que es la misma definición que persiste la migración.
"""

from enum import Enum

from app.models.enums import (
    EstadoHabitacion,
    EstadoLimpieza,
    EstadoReserva,
    MetodoPago,
    TipoDocumento,
    TipoHabitacion,
    TipoPago,
    TipoTurno,
)
from app.models.usuario import RolUsuario
from app.schemas.catalogo import CatalogoRead


def _catalogo(nombre: str, etiqueta: str, enumeracion: type[Enum]) -> CatalogoRead:
    return CatalogoRead(
        nombre=nombre,
        etiqueta=etiqueta,
        valores=[miembro.value for miembro in enumeracion],
    )


CATALOGOS: dict[str, CatalogoRead] = {
    catalogo.nombre: catalogo
    for catalogo in (
        _catalogo("roles", "Roles de usuario", RolUsuario),
        _catalogo("tipos_habitacion", "Tipos de habitacion", TipoHabitacion),
        _catalogo("estados_habitacion", "Estados de habitacion", EstadoHabitacion),
        _catalogo("estados_limpieza", "Estados de limpieza", EstadoLimpieza),
        _catalogo("estados_reserva", "Estados de reserva", EstadoReserva),
        _catalogo("metodos_pago", "Metodos de pago", MetodoPago),
        _catalogo("tipos_pago", "Tipos de pago", TipoPago),
        _catalogo("tipos_turno", "Tipos de turno", TipoTurno),
        _catalogo("tipos_documento", "Tipos de documento", TipoDocumento),
    )
}


def listar_catalogos() -> list[CatalogoRead]:
    return list(CATALOGOS.values())


def obtener_catalogo(nombre: str) -> CatalogoRead | None:
    return CATALOGOS.get(nombre)