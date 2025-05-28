import asyncio

import requests
from aiohttp import ClientSession
from whatsapp_chatbot_python import GreenAPIBot, Notification, BaseStates
from whatsapp_chatbot_python.filters import TEXT_TYPES
from enum import Enum

from wathsapp_bot.config import ID_INSTANCE, API_TOKEN
from wathsapp_bot.states.user_state import SearchState
# Убедитесь, что функция синхронная
from wathsapp_bot.utils.movie_pars import pars_json_kino_poisk
from wathsapp_bot.utils.send_func import *



bot = GreenAPIBot(ID_INSTANCE, API_TOKEN)



#
# # Добавим отладочный вывод
# print("Available states:", [state.value for state in SearchState])

# Декоратор для Очистки Состояния
@bot.router.message(command="cancel")
def cancel_handler(notification: Notification) -> None:
    sender = notification.sender
    print(f"\n--- Cancel handler for {sender} ---")
    print("Current state:", notification.state_manager.get_state(sender))

    notification.state_manager.delete_state(sender)
    notification.answer("Bye")

    print("State after cancel:", notification.state_manager.get_state(sender))

# @bot.router.message(command="search")
@bot.router.message(text_message='000')
def pars_handler(notification: Notification):
    sender = notification.sender
    print(f"\n--- Search command from {sender} ---")

    notification.answer("Введите название фильма.")
    notification.state_manager.set_state(sender, SearchState.SEARCH)

    print("State after set:", notification.state_manager.get_state(sender))

@bot.router.message(state=SearchState.SEARCH.value, type_message=TEXT_TYPES)
def pars_search_handler(notification: Notification):
    sender = notification.sender
    notification.answer("Сбор данных подождите пожалуйста! ")


    print(f"\n--- Search state handler for {sender} ---")
    print("Current state:", notification.state_manager.get_state(sender))

    query = notification.message_text
    print("Received query:", query)

    try:
        # Сохраняем текст от пользователя
        query = notification.message_text
        data =  asyncio.run(pars_json_kino_poisk(query))
        print("Parser result:", data)

        if not data or not data.get("movies"):
            notification.answer("Фильмы не найдены")
            return

        asyncio.run(send_image_and_message(number_user=sender, dct_send=data))
    except (TypeError, ValueError, AttributeError):
        notification.answer("Фильмы не найдены")
    finally:
        notification.state_manager.delete_state(sender)
        print("State after processing:", notification.state_manager.get_state(sender))


print("\nStarting bot...")
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    try:
        bot.run_forever()
    except KeyboardInterrupt:
        print('Выключение Бота')
    except Exception as ex:
        print(f'Ошибка: {ex}')