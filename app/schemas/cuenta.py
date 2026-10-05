from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_serializer

from app.models.enums import MetodoPago, TipoPago
from app.schemas.base import CamelCaseSchema


class CuentaDetalleConsumo(CamelCaseSchema):
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

    @field_serializer("precio_unitario", when_used="json")
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)


class CuentaDetallePago(CamelCaseSchema):
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


class CuentaRead(CamelCaseSchema):
    total_alojamiento: Decimal = Field(description="Noches x precio_noche_aplicado")
    total_consumos_vigentes: Decimal = Field(description="Suma de consumos no anulados")
    total_pagos_vigentes: Decimal = Field(
        description="Suma de pagos no anulados (excluye REEMBOLSO)"
    )
    saldo_pendiente: Decimal = Field(
        description="total_alojamiento + total_consumos_vigentes - total_pagos_vigentes"
    )
    detalle_consumos: list[CuentaDetalleConsumo]
    detalle_pagos: list[CuentaDetallePago]

    @field_serializer(
        "total_alojamiento",
        "total_consumos_vigentes",
        "total_pagos_vigentes",
        "saldo_pendiente",
        when_used="json",
    )
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)