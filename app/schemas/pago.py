from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_serializer

from app.models.enums import MetodoPago, TipoPago
from app.schemas.base import CamelCaseSchema


class PagoCreate(CamelCaseSchema):
    monto: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    metodo: MetodoPago
    tipo: TipoPago
    referencia: str | None = Field(default=None, max_length=100)
    fecha_pago: datetime | None = None


class PagoAnular(CamelCaseSchema):
    motivo_anulacion: str = Field(min_length=1, max_length=500)


class PagoRead(CamelCaseSchema):
    id: int
    reserva_id: int
    monto: Decimal
    metodo: MetodoPago
    tipo: TipoPago
    referencia: str | None = None
    anulado: bool
    motivo_anulacion: str | None = None
    fecha_pago: datetime
    registrado_por: int
    anulado_por: int | None = None
    anulado_en: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("monto", when_used="json")
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)