import asyncio
import logging
import threading


from whatsapp_chatbot_python import GreenAPIBot, Notification
from whatsapp_chatbot_python.filters import TEXT_TYPES

from wathsapp_bot.config import ID_INSTANCE, API_TOKEN
from wathsapp_bot.states.user_state import SearchState
from wathsapp_bot.utils.async_bot_manager import start_async_loop, run_async
from wathsapp_bot.utils.message_text import welcome_message, subscription_is_not_text, profile_message, commands_text
from wathsapp_bot.utils.movie_pars import pars_json_kino_poisk
from wathsapp_bot.utils.send_func import *
from wathsapp_bot.utils.shaduler_func import setup_scheduler

from database.crud import async_add_user, check_subscription, get_all_users, get_user, add_plas_subscriptions
from database.db import init_db



bot = GreenAPIBot(ID_INSTANCE, API_TOKEN)


# Работа с меню
@bot.router.message(text_message='000')
def message_handler(notification: Notification) -> None:
    sender = notification.sender
    run_async(handle_user_message(sender, notification))

@bot.router.message(text_message='0')
def add_all_handler(notification: Notification):
    admins = ['79958042251@c.us', '79323056361@c.us']
    if notification.sender in admins:
        notification.answer('Подписки у всех пользователей продлена на 5 дней')
        run_async(add_plas_subscriptions(5))

# Рабочая Версия кода
@bot.router.poll_update_message()
def start_poll_handler(notification: Notification) -> None:
    """
    Обработчик обновлений опросов (Poll).
    Вызывается при выборе пользователем варианта в опросе.

    📌 Возможности:
    - Запускает асинхронную обработку выбранного пункта.
    - Не блокирует основной поток благодаря `run_async`.
    - FSM: Устанавливает состояние `SEARCH` при выборе "Поиск Фильмов".
    - Отправляет данные профиля при выборе "Личный Кабинет".

    ⚠️ Защита от повторной обработки опросника реализована через флаг `data_warning`.
    """

    sender = notification.sender
    votes = notification.event["messageData"]["pollMessageData"]["votes"]

    async def handle_poll():
        """
        Асинхронная функция для обработки голосов из опроса.
        Выполняется в отдельной задаче через run_async (через очередь).
        """
        try:
            for vote_data in votes:
                voters = vote_data["optionVoters"]
                if not voters:
                    continue  # Пропускаем пункты без голосов

                option_name = vote_data['optionName']

                # 1. Поиск фильмов
                if option_name == '1. Поиск Фильмов':
                    await send_message_text(sender, "🔍 Введите название фильма")
                    notification.state_manager.set_state(sender, SearchState.SEARCH)

                # 2. Личный кабинет
                elif option_name == '2. Личный Кабинет':
                    user = await get_user(sender)
                    status = 'Активный' if user.get('is_active', False) else 'Не Активный'

                    txt = profile_message(
                        whatsapp_id=user.get('whatsapp_id'),
                        created_at=user.get('created_at'),
                        day_count=user.get('day_count'),
                        is_active=status
                    ).strip()

                    await send_message_text(sender, txt)

                # Остальные варианты
                else:
                    await send_message_text(sender, 'Пока не готово')

        except Exception as ex:
            print(f'❌ Ошибка при обработке опроса: {ex}')


    # Запускаем задачу асинхронно (без блокировки основного потока)
    run_async(handle_poll())


# Обработка состояния поиска фильмов
@bot.router.message(state=SearchState.SEARCH.value, type_message=TEXT_TYPES)
def pars_search_handler(notification: Notification):
    sender = notification.sender
    run_async(process_search(sender, notification.message_text, notification))



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Запуск асинхронного цикла в фоне
    threading.Thread(target=start_async_loop, daemon=True).start()

    # Инициализация БД
    asyncio.run(init_db())

    # Планировщик (можно оставить sync)
    setup_scheduler(hour=0, minute=0)

    try:
        bot.run_forever()
    except KeyboardInterrupt:
        print("⛔ Бот остановлен")
