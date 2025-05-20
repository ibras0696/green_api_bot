import asyncio
from pprint import pprint

from playwright.async_api import async_playwright, Browser
from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def get_movie(search: str, session: ClientSession) -> dict[str, list]:
    '''
    Сбор данных с одного источника для получение данных: Названий, Ссылок не прямых, Фото Фильма
    :param search: Поиск Кино
    :param session: Сессия запросов

    :return: Словарь в виде {name: [Название фильмов], link_block: [Не прямые ссылки на фильмы], img: Фотографии}
    '''
    url = f'https://w140.zona.plus/search/{search}'
    dct = {
        'name': [],
        'link_block': [],
        'img': []
    }
    async with session.get(url=url) as response:
        if response.status >= 200 and response.status <= 299:
            text_resp = await response.text()

            soup = BeautifulSoup(text_resp, 'lxml')
            data = soup.find('ul', class_='results').find_all('li', class_='results-item-wrap')

            if data is None:
                return dct

            for block_movie in data:
                # Название Фильма
                name = block_movie.find('div', class_='results-item-title').text
                # Ссылка для получение фильма но через доп функцию с html
                link_block = 'https://w140.zona.plus' + block_movie.find('a', class_='results-item').get('href')
                # Фото
                res_img = block_movie.find('div', class_='result-item-preview fadeIn animated').get('style')[22:]
                img = ''
                for i in res_img:
                    if i != ')':
                        img += i
                    else:
                        break

                dct['name'].append(name)
                dct['link_block'].append(link_block)
                dct['img'].append(img)

            return dct
        else:
            raise f'Ошибка статуса кода: {response.status}'


async def get_movie_result(search: str) -> dict[str, list]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
            "Sec-CH-UA-Mobile": "?1",
            "Viewport-Width": "360",
        }

        async with ClientSession(headers=headers) as session:
            dct_movie = await get_movie(search, session)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            # Создаём отдельную страницу для каждой ссылки
            tasks = [process_single_url(p, browser, url) for url in dct_movie.get('link_block', [])]
            result_links = await asyncio.gather(*tasks)
            dct_movie['links'] = result_links


        return dct_movie

    except Exception as ex:
        raise f'Ошибка Парсера: {ex}'
    finally:
        await browser.close()


async def process_single_url(p, browser: Browser, url: str) -> str:
    page = await browser.new_page()

    try:
        await page.goto(url.strip(), wait_until="domcontentloaded")

        video_element = await page.wait_for_selector("video#player_html5_api", timeout=10000)
        if not video_element:
            return "Объект Отсутствует"

        src_url = await video_element.get_attribute("src")
        return src_url or "Видео не найдено (пустой src)"

    except Exception as e:
        return f"Ошибка: {str(e)}"
    finally:
        await page.close()




# Точка входа
if __name__ == "__main__":
    pprint(asyncio.run(get_movie_result("Ривердэйл")))