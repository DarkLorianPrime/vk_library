import os

from vk_dark_library.VKBotLongPoll import VKLongPoll, LoadConfig, GetApi, NEW
from vk_dark_library.VKDebugMode import InitializeDebugger

LoadConfig(os.getcwd(), "config")
vk = GetApi()


def main():
    for vk_object in VKLongPoll().listen():
        if vk_object.type == NEW:
            
            if vk_object.text == "hello":
                vk.messages.send(**vk_object.send_id, message="И тебе привет, путник!", random_id=0)


if __name__ == "__main__":
    debugger = InitializeDebugger(main)
    debugger.start_debug()
