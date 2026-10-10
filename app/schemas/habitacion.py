from datetime import datetime
from decimal import Decimal

from pydantic import Field, computed_field, field_serializer

from app.core.config import settings
from app.models.habitacion import EstadoHabitacion, EstadoLimpieza, TipoHabitacion
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


class HabitacionLimpieza(CamelCaseSchema):
    limpieza: EstadoLimpieza


class HabitacionImagenRead(CamelCaseSchema):
    id: int
    orden: int
    es_principal: bool
    ruta: str = Field(exclude=True)

    @computed_field
    @property
    def url(self) -> str:
        return f"{settings.media_url_prefix}/{self.ruta}"


class HabitacionRead(HabitacionCreate):
    id: int
    limpieza: EstadoLimpieza
    created_at: datetime
    updated_at: datetime
    imagenes: list[HabitacionImagenRead] = []

    @field_serializer("precio_por_noche", when_used="json")
    def serialize_precio_por_noche(self, value: Decimal) -> float:
        return float(value)

    @computed_field
    @property
    def imagen_principal_url(self) -> str | None:
        for imagen in self.imagenes:
            if imagen.es_principal:
                return imagen.url
        return None