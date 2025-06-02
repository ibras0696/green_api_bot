import asyncio
import logging

from whatsapp_chatbot_python import GreenAPIBot, Notification
from whatsapp_chatbot_python.filters import TEXT_TYPES

from wathsapp_bot.config import ID_INSTANCE, API_TOKEN
from wathsapp_bot.states.user_state import SearchState
from wathsapp_bot.utils.message_text import welcome_message, subscription_is_not_text, profile_message, commands_text
from wathsapp_bot.utils.movie_pars import pars_json_kino_poisk
from wathsapp_bot.utils.send_func import *
from wathsapp_bot.utils.shaduler_func import setup_scheduler

from database.crud import async_add_user, check_subscription, get_all_users, get_user
from database.db import init_db



bot = GreenAPIBot(ID_INSTANCE, API_TOKEN)



#
# # Добавим отладочный вывод
# print("Available states:", [state.value for state in SearchState])

# Декоратор для Очистки Состояния
# @bot.router.message(command="cancel")
# def cancel_handler(notification: Notification) -> None:
#     sender = notification.sender
#     print(f"\n--- Cancel handler for {sender} ---")
#     print("Current state:", notification.state_manager.get_state(sender))
#
#
#     notification.answer("Bye")
#
#     print("State after cancel:", notification.state_manager.get_state(sender))

# Работа с профиля
@bot.router.message(text_message='0')
def profile_cmd(notification: Notification):
    sender = notification.sender
    # Очистка прежних состояний
    notification.state_manager.delete_state(sender)
    # Получение данных с БД
    user = asyncio.run(get_user(sender))
    # Проверка Статуса
    status = 'Активный' if user.get('is_active', False) else 'Не Активный'
    # Основной отправочный текст
    txt = profile_message(whatsapp_id=user.get('whatsapp_id'),
                          created_at=user.get('created_at'), day_count=user.get('day_count'), is_active=status).strip()

    asyncio.run(send_message_text(sender, txt))

# Работа с покупкой подписки
@bot.router.message(text_message='00')

# Работа с поиском
@bot.router.message(text_message='000')
def pars_handler(notification: Notification):
    sender = notification.sender
    # Очистка прежних состояний
    notification.state_manager.delete_state(sender)
    # Добавление пользователя
    result = asyncio.run(async_add_user(whatsapp_id=sender))
    # Проверка подписки
    check_result = asyncio.run(check_subscription(sender))
    # Если пользователя не было, добавляем и даём 5 дней подписки
    if result:
        # notification.answer(welcome_message)
        asyncio.run(send_message_text(sender, welcome_message))
    elif check_result:
        asyncio.run(send_message_text(sender, "🔍 Введите название фильма"))
        # notification.answer("🔍 Введите название фильма")
        # Ставим Состояние поиска
        notification.state_manager.set_state(sender, SearchState.SEARCH)
    else:
        asyncio.run(send_message_text(sender, subscription_is_not_text))
        # notification.answer(subscription_is_not_text)


@bot.router.message(state=SearchState.SEARCH.value, type_message=TEXT_TYPES)
def pars_search_handler(notification: Notification):
    sender = notification.sender
    # notification.answer("⏳ Сбор данных... Пожалуйста, подождите!")
    asyncio.run(send_message_text(sender, "⏳ Сбор данных... Пожалуйста, подождите!"))
    try:
        # Получение данных с Парсера
        data = asyncio.run(pars_json_kino_poisk(notification.message_text))

        if not data or not data.get("movies"):
            # notification.answer("Фильмы не найдены")
            asyncio.run(send_message_text(sender, "😢 Фильмы не найдены. Попробуйте изменить запрос"))
            return

        asyncio.run(send_image_and_message(number_user=sender, dct_send=data))
    except (TypeError, ValueError, AttributeError):
        asyncio.run(send_message_text(sender, "😢 Фильмы не найдены. Попробуйте изменить запрос"))
        # notification.answer("😢 Фильмы не найдены. Попробуйте изменить запрос")
    finally:
        notification.state_manager.delete_state(sender)
        # notification.answer("🔍 000 – Начать поиск ")
        asyncio.run(send_message_text(sender, commands_text))



async def main():
    # Инициализация БД
    # asyncio.run(init_db())
    await init_db()
    # Установка планировщика apscheduler
    await setup_scheduler(hour=0, minute=0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Инициализация базы
    asyncio.run(init_db())

    # Запуск планировщика
    setup_scheduler(hour=23, minute=24)  # каждый день в 00:00

    try:
        bot.run_forever()
    except KeyboardInterrupt:
        print("⛔ Бот остановлен")

