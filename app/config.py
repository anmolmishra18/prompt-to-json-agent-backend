from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = Field(default="Prompt→JSON Agent Backend")
    DEBUG: bool = Field(default=True)
    # Use SQLite by default so it works out of the box.
    # For Postgres/Supabase, set DATABASE_URL in .env (see .env.example)
    DATABASE_URL: str = Field(default="sqlite:///./app.db")

    class Config:
        env_file = ".env"

settings = Settings()
