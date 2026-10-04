from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import EmailStr, Field, field_validator

from app.models import EstadoReserva, TipoDocumento
from app.schemas.base import CamelCaseSchema

BOGOTA = ZoneInfo("America/Bogota")


def _compactar_texto(valor: str, campo: str) -> str:
    compacto = " ".join(valor.split())
    if not compacto:
        raise ValueError(f"{campo} no puede estar vacio")
    return compacto


class HuespedCreate(CamelCaseSchema):
    tipo_documento: TipoDocumento
    numero_documento: str = Field(pattern=r"^[A-Za-z0-9]{4,20}$")
    nombres: str = Field(min_length=1, max_length=120)
    apellidos: str = Field(min_length=1, max_length=120)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, pattern=r"^\+?\d{7,15}$")
    nacionalidad: str | None = Field(default=None, max_length=80)
    fecha_nacimiento: date | None = None
    direccion: str | None = None
    observaciones: str | None = None

    @field_validator("numero_documento", mode="before")
    @classmethod
    def documento_sin_espacios(cls, valor: object) -> object:
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator("nombres", "apellidos", mode="before")
    @classmethod
    def nombres_sin_espacios_sobrantes(cls, valor: object, info) -> object:
        if isinstance(valor, str):
            return _compactar_texto(valor, info.field_name)
        return valor

    @field_validator("fecha_nacimiento")
    @classmethod
    def nacimiento_no_futuro(cls, valor: date | None) -> date | None:
        if valor is not None and valor > datetime.now(BOGOTA).date():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        return valor


class HuespedUpdate(HuespedCreate):
    pass


class HuespedRead(HuespedCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class HuespedResumen(CamelCaseSchema):
    id: int
    nombres: str
    apellidos: str
    tipo_documento: TipoDocumento
    numero_documento: str


class HuespedPagina(CamelCaseSchema):
    items: list[HuespedRead]
    total: int
    pagina: int
    tamano: int


class ReservaDeHuespedRead(CamelCaseSchema):
    id: int
    codigo: str
    habitacion_id: int
    fecha_entrada: date
    fecha_salida: date
    estado: EstadoReserva


class ReservaDeHuespedPagina(CamelCaseSchema):
    items: list[ReservaDeHuespedRead]
    total: int
    pagina: int
    tamano: int
