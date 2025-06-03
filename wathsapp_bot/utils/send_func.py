import asyncio
from collections import defaultdict

from aiohttp import ClientSession
from whatsapp_chatbot_python import Notification

from database.crud import async_add_user, check_subscription
from wathsapp_bot.config import URL_SEND_IMG, URL_SEND_TEXT
from wathsapp_bot.states.user_state import SearchState
from wathsapp_bot.utils.message_text import welcome_message, subscription_is_not_text, commands_text
from wathsapp_bot.utils.movie_pars import pars_json_kino_poisk


# Функция для отправки фото
async def send_message_img(chat_id: str | int = None, image_url: str = None, caption: str = None, session: ClientSession = None) -> bool:
    '''
    Отправка Одного сообщения: текста, фотки по url пользователю ватцап
    :param chat_id: номер владельца например: 79323056361@c.us
    :param image_url: ссылка на url
    :param caption: Текст для отправки
    :param session: Ассинхронная Сессия
    :return: True если сообщение отправилось если нет False
    '''
    payload = {
        "chatId": f"{chat_id}",
        "urlFile": image_url,
        "fileName": 'prosto',
        "caption": caption
    }
    headers = {
        'Content-Type': 'application/json'
    }
    async with session.post(URL_SEND_IMG, headers=headers, json=payload) as response:
        if response.status == 200:
            return True
    return False

# Функция для отправки Текста
async def send_message_text(chat_id: str | int = None, message_text: str = None) -> bool:
    '''
    Отправка Одного сообщения: текста, фотки по url пользователю ватцап
    :param chat_id: номер владельца например: 79323056361@c.us
    :param message_text: Текст для отправки
    :return: True если сообщение отправилось если нет False
    '''
    payload = {
        "chatId": f"{chat_id}",
        "message": message_text,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    async with ClientSession() as session:
        async with session.post(URL_SEND_TEXT, headers=headers, json=payload) as response:
            if response.status == 200:
                return True
        print(response.status)
        return False


async def send_image_and_message(number_user: int | str, dct_send: dict[str, list]) -> bool | str:
    '''
    Ассинхронная передача сообщений в ватцап
    :param number_user: Номер Пользователя ватцап
    :param dct_send: Словарь со значениями new_dct = {
            'movies': [], # Название фильмов
            'api_urls': [], # url по апи
            'imgs': [] # Ссылки на качественные фотографии
        }
    :return: True если все сообщения отправились и Ошибка в случае Exception
    '''
    async with ClientSession() as session:
        try:
            tasks = [send_message_img(chat_id=number_user,
                                  image_url=dct_send['imgs'][i],
                                  caption=f"Фильм: {dct_send['movies'][i]}"
                                          f"\nСсылка: {dct_send['api_urls'][i]}\n",
                                  session=session
                                  ) for i in range(len(dct_send["movies"]))]
            await asyncio.gather(*tasks)
        except Exception as ex:
            return f'Ошибка: {ex} \nПри отправке сообщении с img в ватцап'
        else:
            return True



async def handle_user_message(sender: str, notification: Notification | None = None) -> None:
    """
    📦 Обработка пользователя при первом входе по команде '000':
    - Если пользователь новый — добавляется и получает 5 дней подписки.
    - Если подписка есть — открывается опросник.
    - Если подписки нет — предлагается купить.

    :param sender: WhatsApp ID пользователя (например, '79001234567@c.us')
    :param notification: Объект уведомления (нужен для отправки опросника)
    """

    # 🔄 Пытаемся добавить пользователя (если уже есть — просто вернёт False)
    is_new = await async_add_user(whatsapp_id=sender)


    # 🎉 Новый пользователь
    if is_new:
        await send_message_text(sender, welcome_message)
        notification.state_manager.set_state(sender, SearchState.SEARCH)
        return

    # 📌 показываем опросник
    if notification:
        sender_data = notification.event.get("senderData", {})
        sender_name = sender_data.get("senderName", "пользователь")

        notification.answer_with_poll(
            f"Привет, {sender_name}\n\n🔍 Введите название фильма",
            [
                {"optionName": "1. Поиск Фильмов"},
                {"optionName": "2. Личный Кабинет"},
                {"optionName": "3. Покупка Подписки"},
            ]
        )


async def process_search(sender: str, query: str, notification: Notification) -> None:
    """
    🔎 Обработка запроса пользователя на поиск фильма.

    📌 Функция:
    - Отправляет сообщение "Сбор данных..."
    - Парсит данные из внешнего источника по запросу пользователя
    - Отправляет найденные фильмы (или сообщение об отсутствии)
    - Очищает состояние FSM и завершает опросник

    :param sender: WhatsApp ID пользователя (например, '79001234567@c.us')
    :param query: Поисковой запрос (текст от пользователя)
    :param notification: Объект уведомления от Green API, используется для управления состояниями
    """
    has_subscription = await check_subscription(user_id=sender)
    if has_subscription is not True:
        await send_message_text(sender, subscription_is_not_text)
        # ✅ Очистка состояния FSM
        notification.state_manager.delete_state(sender)
        return

    # ⏳ Уведомляем о начале поиска
    await send_message_text(sender, "⏳ Сбор данных... Пожалуйста, подождите!")

    try:
        # 📡 Получаем данные с внешнего API/парсера
        data = await pars_json_kino_poisk(query)

        # ❌ Если фильмы не найдены
        if not data or not data.get("movies"):
            await send_message_text(sender, "😢 Фильмы не найдены. Попробуйте изменить запрос")
            return

        # 🖼 Отправка изображений и описаний
        await send_image_and_message(number_user=sender, dct_send=data)

    except (TypeError, ValueError, AttributeError):
        # 🛑 Обработка ошибок в ответе или парсинге
        await send_message_text(sender, "😢 Фильмы не найдены. Попробуйте изменить запрос")

    finally:
        sender_data = notification.event.get("senderData", {})
        sender_name = sender_data.get("senderName", "пользователь")
        # ✅ Очистка состояния FSM
        notification.state_manager.delete_state(sender)

        # 📋 Отправка командного меню
        notification.answer_with_poll(
            f"Привет, {sender_name}\n\n🔍 Меню Бота",
            [
                {"optionName": "1. Поиск Фильмов"},
                {"optionName": "2. Личный Кабинет"},
                {"optionName": "3. Покупка Подписки"},
            ]
        )


# print(asyncio.run(send_message_text('79958042251@c.us', 'йоу')))