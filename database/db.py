import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.models import Base

# Абсолютный путь к БД — работает независимо от того, откуда запущен бот
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # корень проекта
DB_PATH = os.path.join(BASE_DIR, "database", "DataBase.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"


engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,                 # Привязываем движок к сессии
    class_=AsyncSession,        # Используем асинхронную версию сессии
    expire_on_commit=False      # Данные не сбрасываются после commit
)

async def init_db():
    """
    Инициализация базы данных: создание таблиц.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)