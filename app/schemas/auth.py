from pydantic import ConfigDict, EmailStr

from app.models.usuario import RolUsuario
from app.schemas.base import CamelCaseSchema


class LoginRequest(CamelCaseSchema):
    username: str
    email: str
    password: str

    model_config = ConfigDict(extra="ignore")


class LoginResponse(CamelCaseSchema):
    token: str
    token_type: str = "bearer"
    id: int
    username: str
    email: EmailStr
    nombre: str
    role: RolUsuario