from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.habitacion import Habitacion


class HabitacionImagen(Base):
    __tablename__ = "habitacion_imagenes"
    __table_args__ = (
        Index(
            "uq_habitacion_imagenes_principal",
            "habitacion_id",
            unique=True,
            postgresql_where=text("es_principal"),
            sqlite_where=text("es_principal"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    habitacion_id: Mapped[int] = mapped_column(
        ForeignKey("habitaciones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ruta: Mapped[str] = mapped_column(String(255), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    es_principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    habitacion: Mapped["Habitacion"] = relationship(back_populates="imagenes")
