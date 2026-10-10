from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Numeric, Text, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoHabitacion, EstadoLimpieza, TipoHabitacion

if TYPE_CHECKING:
    from app.models.habitacion_imagen import HabitacionImagen


class Habitacion(Base):
    __tablename__ = "habitaciones"
    __table_args__ = (
        CheckConstraint("numero > 0", name="numero_positivo"),
        CheckConstraint("capacidad >= 1", name="capacidad_positiva"),
        CheckConstraint("precio_por_noche > 0", name="precio_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(unique=True, nullable=False)
    tipo: Mapped[TipoHabitacion] = mapped_column(
        SqlEnum(
            TipoHabitacion,
            name="tipo_habitacion",
            values_callable=lambda enum_values: [item.value for item in enum_values],
        ),
        nullable=False,
    )
    capacidad: Mapped[int] = mapped_column(nullable=False)
    precio_por_noche: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    estado: Mapped[EstadoHabitacion] = mapped_column(
        SqlEnum(
            EstadoHabitacion,
            name="estado_habitacion",
            values_callable=lambda enum_values: [item.value for item in enum_values],
        ),
        default=EstadoHabitacion.DISPONIBLE,
        nullable=False,
    )
    limpieza: Mapped[EstadoLimpieza] = mapped_column(
        SqlEnum(
            EstadoLimpieza,
            name="estado_limpieza",
            values_callable=lambda enum_values: [item.value for item in enum_values],
        ),
        default=EstadoLimpieza.LIMPIA,
        nullable=False,
    )
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    imagenes: Mapped[list["HabitacionImagen"]] = relationship(
        back_populates="habitacion",
        cascade="all, delete-orphan",
        order_by="HabitacionImagen.orden",
    )