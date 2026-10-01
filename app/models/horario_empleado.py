from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Text, Time, UniqueConstraint, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import TipoTurno


class HorarioEmpleado(Base):
    __tablename__ = "horarios_empleado"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "fecha", "hora_inicio", name="uq_horarios_usuario_fecha_inicio"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    tipo_turno: Mapped[TipoTurno] = mapped_column(
        SqlEnum(
            TipoTurno,
            name="tipo_turno",
            values_callable=lambda enum_values: [item.value for item in enum_values],
        ),
        nullable=False,
    )
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )