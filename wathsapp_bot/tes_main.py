import asyncio

from whatsapp_chatbot_python import GreenAPIBot, Notification, BaseStates
from whatsapp_chatbot_python.filters import TEXT_TYPES

from wathsapp_bot.utils.movie_pars import pars_json_kino_poisk

ID_INSTANCE = "1103197563"
API_TOKEN = "f7aabbc0ed3b44b9b1d89a90744b3d7b2e88a73f91fc4fb984"



bot = GreenAPIBot(
    ID_INSTANCE, API_TOKEN
)

class SearchState(BaseStates):
    SEARCH = 'search'


@bot.router.message(command="cancel")
def cancel_handler(notification: Notification) -> None:
    sender = notification.sender

    state = notification.state_manager.get_state(sender)
    if not state:
        return None
    else:
        notification.state_manager.delete_state(sender)

        notification.answer("Bye")

@bot.router.message(command="message")
def message_handler(notification: Notification) -> None:
    sender_data = notification.event["senderData"]
    sender_name = sender_data["senderName"]
    print(sender_data)
    print(sender_name)
    print(notification.event)
    notification.answer(
        (
            f"Hello, {sender_name}. Here's what I can do:\n\n"
            "1. Report a problem\n"
            "2. Show office address\n"
            "3. Show available rates\n"
            "4. Call a support operator\n\n"
            "Choose a number and send to me."
        )
    )

@bot.router.message(command="search")
def pars_handler(notification: Notification):
    sender = notification.sender
    print(sender)

    notification.answer("Введите название фильма.")

    # Ставим состояния запроса фильма
    notification.state_manager.set_state(sender, SearchState.SEARCH.value)


@bot.router.message(state=SearchState.SEARCH.value, type_message=TEXT_TYPES)
def pars_search_handler(notification: Notification):
    sender = notification.sender
    print(sender)
    username = notification.message_text

    txt = notification.message_text
    data = asyncio.run(pars_json_kino_poisk(txt))
    for i in range(len(data['movies'])):
        new_text_answer = (f'Фильм: {data['movies'][i]}'
                           f'\nФото: {data['imgs'][i]}'
                           f'\nСсылка: {data['api_urls'][i]}')
        notification.answer(new_text_answer)

    notification.state_manager.delete_state(sender)

bot.run_forever()

# /search поиск
# @bot.router.message()
# def message_handler(notification: Notification):
#     if notification.message_text.startswith('/search '):
#         txt = notification.message_text.replace('/search', '')
#         data = asyncio.run(pars_json_kino_poisk(txt))
#         for i in range(len(data['movies'])):
#             new_text_answer = (f'Фильм: {data['movies'][i]}'
#                                f'\nФото: {data['imgs'][i]}'
#                                f'\nСсылка: {data['api_urls'][i]}')
#             notification.answer(new_text_answer)



# @bot.router.buttons(command="button")
# def start_handler(notification: Notification) -> None:
#     buttons = [
#         {"buttonId": "report", "buttonText": {"displayText": "Report a problem"}},
#         {"buttonId": "address", "buttonText": {"displayText": "Show address"}},
#         {"buttonId": "rates", "buttonText": {"displayText": "Available rates"}},
#     ]
#     notification.answer_buttons(
#         message="Choose an option below:",
#         buttons=buttons
#     )

#
# @bot.router.message(text_message=["2", "Report a problem"])
# def report_problem_handler(notification: Notification) -> None:
#     notification.answer(
#         "https://github.com/green-api/issues/issues/new", link_preview=False
#     )
#
#
# @bot.router.message(text_message=["2", "Show office address"])
# def show_office_address_handler(notification: Notification) -> None:
#     chat = notification.get_chat()
#
#     notification.api.sending.sendLocation(
#         chatId=chat, latitude=55.7522200, longitude=37.6155600
#     )
#
#
# @bot.router.message(text_message=["3", "Show available rates"])
# def show_available_rates_handler(notification: Notification) -> None:
#     notification.answer_with_file("data/rates.png")
#
#
# @bot.router.message(text_message=["4", "Call a support operator"])
# def call_support_operator_handler(notification: Notification) -> None:
#     notification.answer("Good. A tech support operator will contact you soon.")
#

