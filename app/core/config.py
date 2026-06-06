from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    BACKEND_URL: str
    CLIENT_URL: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENAI_API_KEY: str
    COHERE_API_KEY: str
    MODEL_NAME: str
    EMBEDDING_MODEL: str

    class Config:
        env_file = ".env"


settings = Settings()