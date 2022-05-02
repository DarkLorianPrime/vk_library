import os

from vk_dark_library.VKBotLongPoll import VKLongPoll, LoadConfig, GetApi, NEW
from vk_dark_library.VKCommandHandler import CommandHandler, command_handler, search_command_handler

LoadConfig(os.getcwd(), "config")
vk = GetApi()


@search_command_handler(["hellos", ' | '], ["hi", ' | '])
def custom_hello(raw, splited_text):
    vk.messages.send(**raw.send_id, message=f"Привет, {splited_text[1]}!", random_id=0)


@command_handler("hello?", "hi?")
def standart_hello(raw):
    vk.messages.send(**raw.send_id, message="И тебе привет, хе-хе", random_id=0)


for vk_object in VKLongPoll().listen():
    if vk_object.type == NEW:
        CommandHandler().check_updates(vk_object)
