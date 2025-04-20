from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str
    version: str
    summary: str
    description: str
    contact: str
    license_info: dict
    env: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    postgres_url: str
    allowed_origins: str

settings = Settings()

