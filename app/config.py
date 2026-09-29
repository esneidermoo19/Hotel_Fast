from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hotel PMS API"
    database_url: str = "sqlite:///./hotel_pms.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
