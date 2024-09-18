from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
from app.db.base import Base
from app.auth.models import User
from app.products.models import Product
from app.cart.models import CartItem
from app.core.config import settings

# Конфигурация логгера Alembic
config = context.config

# Читаем URL базы данных из конфигурации
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Если настроен файл конфигурации логгера, используем его
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импортируем модели для создания схем
target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск миграций в оффлайн режиме (без подключения к базе данных)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Асинхронный запуск миграций"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Запуск миграций в онлайн режиме (с подключением к базе данных)"""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())
