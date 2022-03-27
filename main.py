import os

import vk_dark

vk_dark.load_config(os.getcwd(), "config")
vk = vk_dark.get_api()
for vk_object in vk_dark.Main().listen():
    if vk_object.type == vk_dark.NEW:
        if vk_object.text == "hello":
            send_id = vk_dark.user_or_chat(vk_object)
            vk.messages.send(**send_id, message="И тебе привет, путник", random_id=0)