from pydantic import ConfigDict, EmailStr, Field

from app.models.usuario import RolUsuario
from app.schemas.base import CamelCaseSchema


class LoginRequest(CamelCaseSchema):
    username: str
    email: str
    password: str

    model_config = ConfigDict(extra="ignore")


class CambiarPasswordRequest(CamelCaseSchema):
    password_actual: str = Field(min_length=1)
    password_nuevo: str = Field(min_length=8, max_length=128)

    model_config = ConfigDict(extra="ignore")


class RefreshRequest(CamelCaseSchema):
    refresh_token: str = Field(min_length=1)

    model_config = ConfigDict(extra="ignore")


class TokenPair(CamelCaseSchema):
    token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(TokenPair):
    id: int
    username: str
    email: EmailStr
    nombre: str
    role: RolUsuario


class MensajeResponse(CamelCaseSchema):
    mensaje: str
