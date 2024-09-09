from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # Настройки приложения
    APP_NAME: str = "E-commerce Service"
    API_V1_STR: str = "/api/v1"

    # JWT настройки
    SECRET_KEY: str = "supersecretkey"  # Желательно заменить на более безопасное значение
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Время жизни токена в минутах

    # Настройки базы данных
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    class Config:
        env_file = ".env"  # Поддержка загрузки переменных окружения из файла .env


# Создаем экземпляр конфигурации
settings = Settings()
