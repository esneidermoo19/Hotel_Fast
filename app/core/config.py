from urllib.parse import quote, unquote

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "dev-only-insecure-secret-key-please-change"


class Settings(BaseSettings):
    app_name: str = "Hotel PMS API"
    database_url: str = "sqlite:///./hotel_pms.db"
    secret_key: str = DEFAULT_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    login_rate_limit: str = "5/minute"
    cors_origins: list[str] = ["http://localhost:5173"]
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def encode_database_password(cls, value: str) -> str:
        scheme, separator, remainder = value.partition("://")
        if not separator:
            return value
        user_info, at_sign, endpoint = remainder.rpartition("@")
        if not at_sign or ":" not in user_info:
            return value
        username, password = user_info.split(":", 1)
        host, slash, path = endpoint.partition("/")
        encoded_password = quote(unquote(password), safe="")
        normalized = f"{scheme}://{username}:{encoded_password}@{host}"
        return f"{normalized}/{path}" if slash else normalized

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        if self.environment.lower() in {"production", "prod"} and (
            self.secret_key == DEFAULT_SECRET_KEY
            or "REPLACE_WITH" in self.secret_key.upper()
            or len(self.secret_key) < 32
        ):
            raise ValueError("SECRET_KEY debe ser segura y tener al menos 32 caracteres en produccion")
        return self


settings = Settings()