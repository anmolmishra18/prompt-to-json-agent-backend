from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Prompt→JSON Agent Backend"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"

settings = Settings()