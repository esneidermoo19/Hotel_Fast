from pydantic import ConfigDict, EmailStr, Field, model_validator

from app.models.usuario import RolUsuario
from app.schemas.base import CamelCaseSchema


class LoginRequest(CamelCaseSchema):
    username: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    password: str

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="after")
    def validar_identificador(self) -> "LoginRequest":
        if self.username is None and self.email is None:
            raise ValueError("Debes proporcionar username o email")
        return self


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
