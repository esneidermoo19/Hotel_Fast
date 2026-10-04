from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, Text, UniqueConstraint, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import TipoDocumento


class Huesped(Base):
    __tablename__ = "huespedes"
    __table_args__ = (
        UniqueConstraint(
            "tipo_documento", "numero_documento", name="uq_huespedes_tipo_numero"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_documento: Mapped[TipoDocumento] = mapped_column(
        SqlEnum(
            TipoDocumento,
            name="tipo_documento",
            values_callable=lambda enum_values: [item.value for item in enum_values],
        ),
        nullable=False,
    )
    numero_documento: Mapped[str] = mapped_column(String(20), nullable=False)
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    nacionalidad: Mapped[str | None] = mapped_column(String(80), nullable=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )