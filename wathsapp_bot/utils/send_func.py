import asyncio

from aiohttp import ClientSession

from wathsapp_bot.config import URL_SEND


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
    async with session.post(URL_SEND, headers=headers, json=payload) as response:
        if response.status == 200:
            return True
    return False


async def send_image_and_message(number_user: int | str, dct_send: dict[str, list]) -> bool | str:
    '''
    Ассинхронная передача сообщений в ватцап
    :param number_user: Номер Пользователя ватцап
    :param dct_send: Словарь со значениями new_dct = {
            'movies': [], # Название фильмов
            'api_urls': [], # url по апи
            'imgs': [] # Ссылки на качественные фотки
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