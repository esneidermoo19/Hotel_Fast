from datetime import datetime
from decimal import Decimal

from pydantic import Field, computed_field, field_serializer

from app.schemas.base import CamelCaseSchema


class ConsumoCreate(CamelCaseSchema):
    descripcion: str = Field(min_length=1, max_length=200)
    cantidad: int = Field(gt=0)
    precio_unitario: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class ConsumoAnular(CamelCaseSchema):
    motivo_anulacion: str = Field(min_length=1, max_length=500)


class ConsumoRead(CamelCaseSchema):
    id: int
    reserva_id: int
    descripcion: str
    cantidad: int
    precio_unitario: Decimal
    anulado: bool
    registrado_por: int
    anulado_por: int | None = None
    anulado_en: datetime | None = None
    motivo_anulacion: str | None = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def total(self) -> Decimal:
        return self.precio_unitario * self.cantidad

    @field_serializer("precio_unitario", "total", when_used="json")
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)