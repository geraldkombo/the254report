from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "majiwatch-kenya"
    app_env: str = "local"

    database_url: str
    redis_url: str

    api_key_change_me: str
    oracle_signing_secret: str | None = None
    admin_email: str = "geraldshikunyi@gmail.com"
    cors_allow_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    data_dir: str = "/data"
    public_base_url: str = "http://localhost:3000"
    app_auto_migrate: bool = False


settings = Settings()
