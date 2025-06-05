import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # Асинхронный планировщик (подходит для aiogram, FastAPI и т.д.)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger            # Триггер, позволяющий запускать задачи по расписанию (как cron)

from pytz import timezone

from database.crud import decrement_subscriptions, get_all_users, delete_movie_token
from wathsapp_bot.utils.send_func import *


def daily_subscription_whatsapp():
    """
    Синхронная обёртка над асинхронной логикой подписки для планировщика.
    Используется внутри BackgroundScheduler, который не поддерживает async-функции.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def process():
        # Уменьшение подписки
        await decrement_subscriptions()
        # Удаление всех временных ссылок на переадресацию
        await delete_movie_token()
        # Получение всех пользователей
        users = await get_all_users()

        for user in users:
            try:
                whatsapp_id = user.get("whatsapp_id")
                if whatsapp_id:
                    day_count = user.get("day_count")

                    # Уведомление если осталось <= 3 дней
                    #if 0 < day_count <= 3:
                    if day_count == 1:
                        await send_message_text(
                            chat_id=whatsapp_id,
                            message_text=(
                                f"⚠️ Внимание! Подписка заканчивается через {day_count} дня. "
                                f"Продлите сейчас, чтобы не потерять доступ!\n📋 000 – Меню"
                            )
                        )

                    # 🔒 Здесь можно добавить блокировку/отключение, если день = 0

            except Exception as ex:
                print(f"❌ Ошибка при отправке уведомления: {ex}")

    try:
        loop.run_until_complete(process())
    finally:
        loop.close()


def setup_scheduler(hour: int = 0, minute: int = 0):
    """
    Инициализация и запуск синхронного планировщика APScheduler
    """
    scheduler = BackgroundScheduler(timezone=timezone('Europe/Moscow'))

    scheduler.add_job(
        func=daily_subscription_whatsapp,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="decrement_subs",
        replace_existing=True
    )

    scheduler.start()
    print("✅ Планировщик запущен (по МСК) и работает по расписанию")