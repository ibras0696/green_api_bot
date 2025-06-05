import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse

from database.crud import get_movie_token

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI"}


# Переадресация пользователя по домену
@app.get("/get_movie/{movie_token}")
async def redirect_to_movie(movie_token: str):
    data = await get_movie_token(movie_token)
    url = data.get('movie_url')
    if url:
        return RedirectResponse(url=url)
    return f'Срок ссылки истёк'


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# # Подключение шаблонов
# templates = Jinja2Templates(directory="app/templates")
#
# # Роут с токеном фильма
# @app.get("/movie/{movie_token}", response_class=HTMLResponse)
# async def show_movie(request: Request, movie_token: str):
#     # Можно тут из БД что-то достать по movie_token
#     fake_movie = {"title": "Example Movie", "token": movie_token}
#     return templates.TemplateResponse("index.html", {
#         "request": request,
#         "movie": fake_movie
#     })
#