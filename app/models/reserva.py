from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import EstadoReserva


class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("fecha_salida > fecha_entrada", name="ck_reservas_fecha_salida_posterior"),
        CheckConstraint("numero_huespedes >= 1", name="ck_reservas_huespedes_minimo"),
        Index("ix_reservas_habitacion_fechas", "habitacion_id", "fecha_entrada", "fecha_salida"),
        Index("ix_reservas_estado", "estado"),
        Index("ix_reservas_huesped", "huesped_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    huesped_id: Mapped[int] = mapped_column(
        ForeignKey("huespedes.id", ondelete="RESTRICT"), nullable=False
    )
    habitacion_id: Mapped[int] = mapped_column(
        ForeignKey("habitaciones.id", ondelete="RESTRICT"), nullable=False
    )
    fecha_entrada: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_salida: Mapped[date] = mapped_column(Date, nullable=False)
    numero_huespedes: Mapped[int] = mapped_column(nullable=False)
    estado: Mapped[EstadoReserva] = mapped_column(
        SqlEnum(
            EstadoReserva,
            name="estado_reserva",
            values_callable=lambda enum_values: [item.value for item in enum_values],
        ),
        default=EstadoReserva.PENDIENTE,
        nullable=False,
    )
    precio_noche_aplicado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    check_in_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    check_out_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    creada_por: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )