"""Registro de auditoría de acciones sensibles.

`usuario_id` es nullable y la FK usa ON DELETE SET NULL: el historial se
conserva aunque se borre el usuario que lo originó.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    accion: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entidad: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entidad_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    direccion_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )


Index("ix_auditoria_entidad_entidad_id", Auditoria.entidad, Auditoria.entidad_id)
