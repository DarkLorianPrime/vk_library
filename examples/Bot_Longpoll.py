import os

from vk_dark_library.VKBotLongPoll import VKLongPoll, NEW, GetApi, LoadConfig

LoadConfig(os.getcwd(), "config")
vk = GetApi()

for vk_object in VKLongPoll().listen():
    if vk_object.type == NEW:
        if vk_object.text == "hello":
            vk.messages.send(**vk_object.send_id, message="И тебе привет, путник!", random_id=0)