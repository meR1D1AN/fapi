# Базовый образ Python
FROM python:3.12.5-slim

# Устанавливаем зависимости системы для сборки
RUN apt-get update && apt-get install -y build-essential libpq-dev curl

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Устанавливаем директорию для приложения
WORKDIR /app

# Копируем файл pyproject.toml и poetry.lock для установки зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости через Poetry
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

# Копируем всё приложение в контейнер
COPY . .

# Сделать скрипт исполняемым
RUN chmod +x /app/start.sh

# Запуск приложения
CMD ["./start.sh"]

# Expose порт для приложения
EXPOSE 8000
