#!/bin/bash

# Ожидание доступности базы данных
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Проверка, существует ли файл миграции
if [ ! -f /app/migrations/versions/$(alembic history | tail -n 1 | awk '{print $4}') ]; then
  alembic revision --autogenerate -m "Database Creation!"
fi

# Выполнение миграций
alembic upgrade head

# Запуск приложения
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload