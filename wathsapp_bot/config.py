import os
import dotenv

dotenv.load_dotenv()

# id инстейнса
ID_INSTANCE = os.getenv('ID_INSTANCE')
# Токен Ватцап
API_TOKEN = os.getenv('API_TOKEN')
# url отправки фоток
URL_SEND_IMG = os.getenv('URL_SEND_IMG')
# url отправки сообщений
URL_SEND_TEXT = os.getenv('URL_SEND_TEXT')




