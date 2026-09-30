from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_serializer

from app.models.habitacion import EstadoHabitacion, TipoHabitacion
from app.schemas.base import CamelCaseSchema


class HabitacionCreate(CamelCaseSchema):
    numero: int = Field(gt=0)
    tipo: TipoHabitacion
    capacidad: int = Field(ge=1)
    precio_por_noche: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    estado: EstadoHabitacion = EstadoHabitacion.DISPONIBLE
    descripcion: str | None = None


class HabitacionUpdate(HabitacionCreate):
    pass


class HabitacionEstado(CamelCaseSchema):
    estado: EstadoHabitacion


class HabitacionRead(HabitacionCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("precio_por_noche", when_used="json")
    def serialize_precio_por_noche(self, value: Decimal) -> float:
        return float(value)