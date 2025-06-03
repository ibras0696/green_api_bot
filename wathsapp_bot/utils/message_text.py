from datetime import datetime, timedelta

import pytz

welcome_message = """
🎬 Добро пожаловать в Кино Бот! 

Я помогу найти любой фильм и дам прямую ссылку для просмотра.  
Просто введи название, например:  
    → «Интерстеллар»  


✨ Возможности:  
    - Прямая ссылка на фильм (сразу к просмотру)  
    - Качество: 480p, 720p, 1080p  
    - Выбор озвучки: оригинал, дубляж, многоголосый  
    - Минимум рекламы  

🎁 Новым пользователям:  
    5 дней бесплатного доступа!  

📋 Команды:  
    000 – Меню Бота   

Наслаждайся кино! 🎥🍿  
""".strip()

commands_text = '''
📋 Команды:  
    000 – Меню Бота 
'''.strip()
subscription_is_not_text = """
📛 Ваша подписка закончилась

Доступ к боту временно ограничен.
Чтобы восстановить полный доступ:

🔄 Продлите подписку - нажмите 00

После оплаты доступ восстановится автоматически в течение 1 минуты.
""".strip()


def profile_message(whatsapp_id: str, day_count: int, is_active: str, created_at) -> str:
    moscow_tz = pytz.timezone('Europe/Moscow')

    # Преобразуем строку в datetime, если нужно
    if isinstance(created_at, str):
        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')

    # Если дата без timezone, считаем что это UTC (или исходное) и делаем aware
    if created_at.tzinfo is None:
        created_at = pytz.utc.localize(created_at)

    # Переводим во временную зону Москвы
    moscow_date = created_at.astimezone(moscow_tz)

    # Форматируем
    start_formatted = moscow_date.strftime('%d.%m.%Y')
    end_date = moscow_date + timedelta(days=day_count)
    end_formatted = end_date.strftime('%d.%m.%Y')

    return f"""
📅 Ваш профиль

    🆔 WhatsApp: {whatsapp_id}
    📅 Дата регистрации: {start_formatted}
    📛 Дата окончания подписки: {end_formatted}
    🔐 Статус: {is_active}
    ⏳ Дней подписки: {day_count}

🛠 Управление:
    000 – Меню Бота 
"""