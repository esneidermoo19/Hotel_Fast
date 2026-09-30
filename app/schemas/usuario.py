from pydantic import EmailStr

from app.models.usuario import RolUsuario
from app.schemas.base import CamelCaseSchema


class UsuarioRead(CamelCaseSchema):
    id: int
    username: str
    email: EmailStr
    nombre: str
    role: RolUsuario