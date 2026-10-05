from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, field_serializer

from app.core.pagination import Pagina
from app.models import EstadoReserva, TipoHabitacion
from app.schemas.base import CamelCaseSchema
from app.schemas.huesped import HuespedResumen


class HabitacionResumen(CamelCaseSchema):
    id: int
    numero: int
    tipo: TipoHabitacion
    capacidad: int
    precio_por_noche: Decimal

    @field_serializer("precio_por_noche", when_used="json")
    def serialize_precio_por_noche(self, value: Decimal) -> float:
        return float(value)


class ReservaCreate(CamelCaseSchema):
    huesped_id: int = Field(ge=1)
    habitacion_id: int = Field(ge=1)
    fecha_entrada: date
    fecha_salida: date
    numero_huespedes: int = Field(ge=1)
    observaciones: str | None = Field(default=None, max_length=1000)


class ReservaUpdate(CamelCaseSchema):
    huesped_id: int | None = Field(default=None, ge=1)
    habitacion_id: int | None = Field(default=None, ge=1)
    fecha_entrada: date | None = None
    fecha_salida: date | None = None
    numero_huespedes: int | None = Field(default=None, ge=1)
    observaciones: str | None = Field(default=None, max_length=1000)


class ReservaRead(CamelCaseSchema):
    id: int
    codigo: str
    huesped: HuespedResumen
    habitacion: HabitacionResumen
    fecha_entrada: date
    fecha_salida: date
    numero_huespedes: int
    estado: EstadoReserva
    precio_noche_aplicado: Decimal
    total_estimado: Decimal
    observaciones: str | None
    motivo_cancelacion: str | None
    check_in_real: datetime | None
    check_out_real: datetime | None
    creada_por: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("precio_noche_aplicado", "total_estimado", when_used="json")
    def serialize_montos(self, value: Decimal) -> float:
        return float(value)


class ReservaFiltros(CamelCaseSchema):
    pagina: int = 1
    tamano: int = 20
    estado: EstadoReserva | None = None
    habitacion_id: int | None = None
    huesped_id: int | None = None
    desde: date | None = None
    hasta: date | None = None


ReservaPagina = Pagina[ReservaRead]