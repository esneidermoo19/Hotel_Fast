from urllib.parse import quote, unquote

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "dev-only-insecure-secret-key-please-change"
DEVELOPMENT_ENVIRONMENTS = {"development", "dev", "test", "testing"}
UNSAFE_SECRET_KEY_MARKERS = ("REPLACE_WITH", "CHANGE_ME", "TODO")


class Settings(BaseSettings):
    app_name: str = "Hotel PMS API"
    environment: str
    database_url: str | None = None
    secret_key: str = DEFAULT_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    cors_origins: list[str] = ["http://localhost:5173"]
    login_rate_limit_per_minute: int = 5
    rate_limit_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def encode_database_password(cls, value: str | None) -> str | None:
        if value is None:
            return value

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
    def validate_environment(self) -> "Settings":
        environment = self.environment.strip().lower()
        if not environment:
            raise ValueError("ENVIRONMENT es obligatorio (development, test o production)")
        if environment not in DEVELOPMENT_ENVIRONMENTS:
            if not self.database_url:
                raise ValueError(
                    "DATABASE_URL es obligatoria fuera de development y test; "
                    "no se permite SQLite silencioso"
                )
            self._validate_secret_key_for_deployment()
        return self

    def _validate_secret_key_for_deployment(self) -> None:
        if self.secret_key == DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY por defecto rechazada; define una clave propia con "
                "python -c \"import secrets; print(secrets.token_urlsafe(48))\""
            )
        if any(marker in self.secret_key.upper() for marker in UNSAFE_SECRET_KEY_MARKERS):
            raise ValueError("SECRET_KEY contiene un marcador sin reemplazar (REPLACE_WITH)")
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")

    @property
    def is_development(self) -> bool:
        return self.environment.strip().lower() in DEVELOPMENT_ENVIRONMENTS

    @property
    def is_production(self) -> bool:
        return not self.is_development

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return "sqlite:///./hotel_pms.db"


settings = Settings()
