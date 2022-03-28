import os

from vk_dark_library.VKBotLongPoll import VKLongPoll, NEW, user_or_chat, load_config, get_api
from vk_dark_library.VKCommandHandler import CommandHandler

load_config(os.getcwd(), "config")
vk = get_api()

for vk_object in VKLongPoll().listen():
    if vk_object.type == NEW:
        CommandHandler().check_updates(vk_object)
        if vk_object.text == "hello":
            send_id = user_or_chat(vk_object)
            vk.messages.send(**send_id, message="И тебе привет, путник!", random_id=0)
