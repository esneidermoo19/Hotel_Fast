from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from app.core.pagination import Pagina
from app.core.passwords import mensaje_de_fortaleza
from app.models.usuario import RolUsuario
from app.schemas.base import CamelCaseSchema


class UsuarioRead(CamelCaseSchema):
    id: int
    username: str
    email: EmailStr
    nombre: str
    role: RolUsuario
    activo: bool
    created_at: datetime
    updated_at: datetime


class UsuarioCrear(CamelCaseSchema):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    email: EmailStr
    nombre: str = Field(min_length=1, max_length=120)
    password: str
    role: RolUsuario = RolUsuario.RECEPCION

    @field_validator("password")
    @classmethod
    def password_fuerte(cls, valor: str) -> str:
        problema = mensaje_de_fortaleza(valor)
        if problema:
            raise ValueError(problema)
        return valor


class UsuarioActualizar(CamelCaseSchema):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=64,
        pattern=r"^[A-Za-z0-9._-]+$",
    )
    email: EmailStr | None = None
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    role: RolUsuario | None = None
    activo: bool | None = None


UsuarioPagina = Pagina[UsuarioRead]
