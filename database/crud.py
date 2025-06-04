import datetime


from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from database.db import async_session
from database.models import User



# Если существует — пропускаем, иначе создаём с +5 дней подписки
async def async_add_user(telegram_id: int = None, whatsapp_id: str = None, days: int = 3) -> bool:
    '''
    Функция для добавления пользователей в бд

    :param telegram_id: Телеграм Айди
    :param whatsapp_id: Ватцап айди
    :param days: количество дней по дефолту 5
    :return: Если пользователь есть возвращает его объект если нет добавляет и даёт 5 дней подписки
    '''
    async with async_session() as session:
        stmt = select(User)
        if telegram_id:
            stmt = stmt.where(User.telegram_id == telegram_id)
        elif whatsapp_id:
            stmt = stmt.where(User.whatsapp_id == whatsapp_id)
        else:
            raise ValueError("Нужно указать либо telegram_id, либо whatsapp_id")

        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            return False  # Пользователь уже есть

        # Создаём нового пользователя с 5 днями подписки
        new_user = User(
            telegram_id=telegram_id,
            whatsapp_id=whatsapp_id,
            day_count=days,
            is_active=True,
            created_at=datetime.datetime.now(datetime.UTC)
        )
        session.add(new_user)
        try:
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return None


# Проверка, активна ли подписка пользователя
async def check_subscription(user_id: int | str) -> bool:
    '''
    Функция проверки подписки пользователя
    :param user_id: int = Telegram_id а str = WhatsApp_id
    :return: True если подписка активна и False если подписка закончилась
    '''
    async with async_session() as session:
        # Проверка по Телеграмм Айди
        if isinstance(user_id, int):
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return user.is_active and user.day_count > 0
            return False
        # Проверка по Ватцап айди
        elif isinstance(user_id, str):
            result = await session.execute(select(User).where(User.whatsapp_id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return user.is_active and user.day_count > 0
            return False


# Уменьшение дней подписки на 1 (например в ежедневном cron)
async def decrement_subscriptions(min_day: int = 1):
    '''
    Функция для уменьшения подписки на 1 день
    :param min_day: Количество для уменьшения дней по дефолту 1
    :return: True при успешном снижении
    '''
    async with async_session() as session:
        result = await session.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()

        for user in users:
            if user.day_count > 0:
                user.day_count -= min_day
            if user.day_count <= 0:
                user.is_active = False

        await session.commit()
        return True

# Уменьшение дней подписки на 1 (например в ежедневном cron)
async def add_plas_subscriptions(add_day: int = 1):
    '''
    Функция для уменьшения подписки на 1 день
    :param add_day: Количество для уменьшения дней по дефолту 1
    :return: True при успешном снижении
    '''
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            user.day_count += add_day
            if user.day_count >= 0:
                user.is_active = True
        await session.commit()
        return True

# Получение всех пользователей и их данных в виде словаря
async def get_all_users(get: int = 1) -> list[dict] | dict[str, list]:
    '''
    Получение всех данных с бд
    :param get: способ получения данных 1 = [{id: '', telegram_id: '', whatsapp_id: '', day_count: '', is_active: '', created_at: ''}]
    | 2 = {id: [], telegram_id: [], whatsapp_id: [], day_count: [], is_active: [] created_at: []}
    :return: список со словарями или словарь со списками
    '''
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        if get == 1:
            return [
                {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "whatsapp_id": user.whatsapp_id,
                    "day_count": user.day_count,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat()
                }
                for user in users
            ]
        else:
            dct = {
                "id": [],
                "telegram_id": [],
                "whatsapp_id": [],
                "day_count": [],
                "is_active": [],
                "created_at": []
            }
            for user in users:
                dct["id"].append(user.id)
                dct["telegram_id"].append(user.telegram_id)
                dct["whatsapp_id"].append(user.whatsapp_id)
                dct["day_count"].append(user.day_count)
                dct["is_active"].append(user.is_active)
                dct["created_at"].append(user.created_at)
            return dct


# Получение всех пользователей и их данных в виде словаря
async def get_user(user_id: int | str) -> dict[str, str | int | bool]:
    '''
    Функция для получения данных одного пользователя
    :param user_id: user_id: int = Telegram_id а str = WhatsApp_id
    :return: {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "whatsapp_id": user.whatsapp_id,
                "day_count": user.day_count,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()}
    '''
    if not isinstance(user_id, (int, str)):
        raise ValueError("user_id должен быть int (Telegram) или str (WhatsApp)")

    async with async_session() as session:
        # Определяем условие поиска в зависимости от типа user_id
        if isinstance(user_id, int):
            stmt = select(User).where(User.telegram_id == user_id)
        else:
            stmt = select(User).where(User.whatsapp_id == user_id)

        result = await session.execute(stmt)
        user = result.scalars().first()
        # Проверка: найден ли пользователь
        if user is None:
            print(f"⚠️ Пользователь с ID {user_id} не найден.")
            return None

        return {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "whatsapp_id": user.whatsapp_id,
                "day_count": user.day_count,
                "is_active": user.is_active,
                "created_at": user.created_at}


# asyncio.run(add_plas_subscriptions(3000))
# asyncio.run(decrement_subscriptions(min_day=3000))
