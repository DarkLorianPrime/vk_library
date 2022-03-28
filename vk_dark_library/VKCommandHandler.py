import json
import re

from .VKBotLongPoll import EventInformation

commands = {}
json_commands = {}
search_commands = {}


def command_handler(*args):
    def decorator(fn):
        for i in args:
            commands[i.lower()] = fn

    return decorator


def search_command_handler(*args):
    def decorator(fn):
        for i in args:
            search_commands[i[0].lower()] = [fn, i[1]]

    return decorator


def json_command_handler(*args):
    def decorator(fn):
        for i in args:
            commands[i.lower()] = fn
            json_commands[i] = fn

    return decorator


class CommandHandler:
    def get_commands(self):
        return commands, json_commands, search_commands

    def check_updates(self, raw: EventInformation):
        lower = raw.text.lower()
        if commands.get(lower) is not None:
            commands[lower](chat_id=raw.chat_id, peer_id=raw.peer_id, text=raw.text, user_id=raw.from_id, raw=raw)
            return

        for i in search_commands:
            if re.search(i, lower):
                splited = raw.text.split(search_commands[i][1])
                if len(splited) > 1:
                    search_commands[i][0](chat_id=raw.chat_id, peer_id=raw.peer_id, text=raw.text, user_id=raw.from_id,
                                          splited=splited, conversation_message_id=raw.conversation_message_id,
                                          raw=raw)
                    return

        if raw.payload is not None:
            payload_data = raw.payload
            load = json.loads(payload_data)
            button = load.get("button")
            if button is None:
                button = "page"
            if load.get("button") is None and load.get(button) is None:
                button = "group"
            if json_commands.get(button) is not None:
                json_commands[button](chat_id=raw.chat_id, peer_id=raw.peer_id, text=raw.text, user_id=raw.from_id,
                                      payload=load.get(button), conversation_message_id=raw.conversation_message_id,
                                      raw=raw)
            return
