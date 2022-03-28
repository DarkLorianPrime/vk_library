import os

from vk_dark_library.VKBotLongPoll import VKLongPoll, load_config, get_api, NEW, user_or_chat
from vk_dark_library.VKCommandHandler import CommandHandler, command_handler, search_command_handler

load_config(os.getcwd(), "config")
vk = get_api()


@search_command_handler(["hellos", ' | '], ["hi", ' | '])
def custom_hello(**kwargs):
    send_id = user_or_chat(kwargs['raw'])
    vk.messages.send(**send_id, message=f"Привет, {kwargs['splited'][1]}!", random_id=0)


@command_handler("hello?", "hi?")
def standart_hello(**kwargs):
    send_id = user_or_chat(kwargs['raw'])
    vk.messages.send(**send_id, message="И тебе привет, хе-хе", random_id=0)


for vk_object in VKLongPoll().listen():
    if vk_object.type == NEW:
        CommandHandler().check_updates(vk_object)
