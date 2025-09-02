from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_DB: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    PINTEREST_EMAIL: str
    PINTEREST_PASSWORD: str
    HEADLESS: bool = True
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
# Create a singleton instance to use across the project

settings = Settings()
