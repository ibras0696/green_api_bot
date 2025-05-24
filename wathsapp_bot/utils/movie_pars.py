import asyncio
import time
from pprint import pprint

from aiohttp import ClientSession
from bs4 import BeautifulSoup

"""
    Парсер zona
async def get_movie(search: str, session: ClientSession, limit: int=3) -> dict[str, list]:
    '''
    Сбор данных с одного источника для получение данных: Названий, Ссылок не прямых, Фото Фильма
    :param limit: Ограничение в объектах
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
            # Прекращение при достижения лимита
            numb_break = 0
            for block_movie in data:
                if numb_break == limit:
                    break
                else:
                    numb_break += 1
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

async def get_movie_result(search: str) -> dict[str, list]:
    try:
        async with ClientSession() as session:
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

"""




async def get_url_kino_poisk(search: str, session: ClientSession):
    '''

    :param search:
    :param session:
    :return:
    '''
    url = f'https://www.kinopoisk.ru/index.php?kp_query={search}'
    async with session.get(url, headers={'User-Agent': 'NOoooo Sahur'}) as response:
        if response.status == 200:
            txt = await response.text()
            soup = BeautifulSoup(txt, 'lxml').find('div', class_='block_left_pad').find_all('div', class_='search_results')
            data = {
                'movies': [],
                'id_movies': [],
                'links': [],
                'imgs': []
            }

            if len(soup) == 0:
                return data

            for i in range(2):
                if i == 0:
                    block_search_results = soup[i]
                    movie = block_search_results.find('p', class_='name').text
                    link = 'https://www.ggpoisk.ru/' + block_search_results.find('a', class_='js-serp-metrika').get('href').replace('cast/#actor', '')
                    id_movie = block_search_results.find('a', class_='js-serp-metrika').get('href').replace('https://www.kinopoisk.ru/images/sm_film/film/', ''
                                                                                                            ).replace('/cast/#actor', '').replace('/film/', '').replace('/sr/1/', '')
                    img = 'https://www.kinopoisk.ru'+block_search_results.find('img').get('title')

                    data['movies'].append(movie)
                    data['id_movies'].append(id_movie)
                    data['links'].append(link)
                    data['imgs'].append(img)

                else:
                    block_search_results = soup[i].find_all('div', class_='element')
                    for elem in block_search_results:
                        movie = elem.find('p', class_='name').text
                        link = 'https://www.ggpoisk.ru/' + elem.find('a',class_='js-serp-metrika').get('href').replace('cast/#actor', '')
                        id_movie = elem.find('a', class_='js-serp-metrika').get('href').replace(
                            'https://www.kinopoisk.ru/images/sm_film/film/', ''
                            ).replace('/cast/#actor', '').replace('/film/', '').replace('/sr/1/', '')
                        img = 'https://www.kinopoisk.ru' + elem.find('img').get('title')

                        data['movies'].append(movie)
                        data['id_movies'].append(id_movie)
                        data['links'].append(link)
                        data['imgs'].append(img)
            return data
        else:
            raise f'Ошибка статуса кода: {response.status}'


async def get_url(url: str, session: ClientSession) -> str | None:
    async with session.get(url) as response:
        try:
            js = await response.json()
            # Более безопасная проверка структуры JSON
            if isinstance(js, list) and len(js) > 2 and isinstance(js[2], dict):
                return js[2].get('iframeUrl')
            return None
        except (AttributeError, KeyError, IndexError, ValueError):
            return None


async def pars_json_kino_poisk(search: str) -> dict[str, list]:
    start = time.time()
    async with ClientSession() as session:
        dct = await get_url_kino_poisk(search, session)
        data_id = dct['id_movies']

        tasks = [get_url(f'https://fbphdplay.top/api/players?kinopoisk={id_kino}', session)
                 for id_kino in data_id]
        lst_api_movie = await asyncio.gather(*tasks)  # Убрали лишнюю обертку в список

        # Очистка данных - более безопасный способ
        new_dct = {
            'movies': [],
            'api_urls': [],
            'imgs': []
        }

        for movie, api_url, img in zip(dct['movies'], lst_api_movie, dct['imgs']):
            if api_url is not None:
                new_dct['movies'].append(movie)
                new_dct['api_urls'].append(api_url)
                new_dct['imgs'].append(img)

    end = time.time()
    print(f'Парсер сработал: {end - start:.2f}')
    return new_dct


pprint(asyncio.run(pars_json_kino_poisk('Пила')))