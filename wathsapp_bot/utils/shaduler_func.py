import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # Асинхронный планировщик (подходит для aiogram, FastAPI и т.д.)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger            # Триггер, позволяющий запускать задачи по расписанию (как cron)
from pytz import timezone

from database.crud import decrement_subscriptions, get_all_users
from wathsapp_bot.utils.send_func import send_message_text

#
# async def daily_subscription_whatsapp():
#     # Уменьшения подписки всех пользователей на 1 день
#     await decrement_subscriptions()
#     # Получения данных с бд
#     data = await get_all_users()
#     for user in data:
#         try:
#             whatsapp_id = user.get('whatsapp_id')
#             if whatsapp_id is not None:
#                 # Количество дней подписки
#                 day_count = user.get('day_count')
#                 if 0 < day_count <= 3:
#                     await send_message_text(chat_id=whatsapp_id,
#                                             message_text=f"⚠️ Внимание! Подписка заканчивается через {day_count} дня. Продлите сейчас, чтобы не потерять доступ!"
#                                                          f"\n📋 00 – Купить подписку  ")
#                 # elif day_count <= 0:
#                 #     await send_message_text(chat_id=whatsapp_id,
#                 #                             message_text="🚫 Ваша подписка закончилась!\n\n📋 00 – Купить новую подписку\n\nНе упустите доступ к любимым фильмам!")
#
#         except Exception as ex:
#             print(f'Ошибка при отправке пуш уведомления об окончании подписки: {ex}')
#             return f'Ошибка при отправке пуш уведомления об окончании подписки: {ex}'
#
#
#
# async def setup_scheduler(hour: int = 0, minute: int = 0):
#     # Создаем экземпляр асинхронного планировщика
#     scheduler = AsyncIOScheduler(timezone=timezone('Europe/Moscow'))
#     # 👇 Здесь можно указать 'Europe/Moscow' если работаешь по МСК
#
#     # Добавляем задачу в планировщик
#     scheduler.add_job(
#         func=daily_subscription_whatsapp,  # 👈 Функция, которую нужно запускать
#         trigger=CronTrigger(hour=hour, minute=minute),  # ⏰ Запускать каждый день в 00:00
#         id="decrement_subs",  # 🆔 Уникальный ID задачи (нужен для управления ей)
#         replace_existing=True  # ✅ Если задача с таким ID уже есть — заменить её
#     )
#
#     # Запускаем планировщик
#     scheduler.start()
#
#     # Для отладки: сообщение в консоль
#     print("✅ Планировщик запущен и работает по расписанию")


def daily_subscription_whatsapp():
    """
    Синхронная обёртка над асинхронной логикой подписки для планировщика.
    Используется внутри BackgroundScheduler, который не поддерживает async-функции.
    """
    print('Запуск Задачи')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def process():
        # Уменьшение подписки
        await decrement_subscriptions()

        # Получение всех пользователей
        users = await get_all_users()

        for user in users:
            try:
                whatsapp_id = user.get("whatsapp_id")
                if whatsapp_id:
                    day_count = user.get("day_count")

                    # Уведомление если осталось <= 3 дней
                    if 0 < day_count <= 3:
                        await send_message_text(
                            chat_id=whatsapp_id,
                            message_text=(
                                f"⚠️ Внимание! Подписка заканчивается через {day_count} дня. "
                                f"Продлите сейчас, чтобы не потерять доступ!\n📋 00 – Купить подписку"
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