import datetime
import importlib
import os
import sys

import requests
import aiofiles
import asyncio
from vk_dark_library.VKErrorLibrary import LongpollConnectionError, ApiMethodError
from vk_dark_library.VKUtils import VKcolors, LONGPOLL_VERSION

File_url = None
vk_api_url = "https://api.vk.com/method/"
v = '5.130'
config = {"v": "5.130", "token": None, "group": None, "debug": None}
NEW = "message_new"


class LoadConfig:
    def __init__(self, path, name):
        if path is not None:
            sys.path.append(path)
            config_file = importlib.import_module(name)
            config.update({"token": config_file.token, "group": config_file.group_id, "debug": config_file.debug})


class EventInformation:
    __slots__ = ["payload", "clear_query", "group_id", "chat_id", "message", "type", "text", "from_id", "peer_id",
                 "conversation_message_id", "send_id", "splited_text", "lower"]

    def __init__(self, raw_query, splited_text=None):
        if config["token"] is None:
            raise Exception("Config not loaded")
        if splited_text is not None:
            self.splited_text = splited_text
        self.clear_query = raw_query["object"]
        self.type = raw_query['type']
        self.group_id = raw_query["group_id"]
        self.chat_id = self.clear_query['message']['peer_id']
        self.from_id = self.clear_query["message"]["from_id"]
        if self.chat_id > 2000000000:
            self.chat_id = self.chat_id - 2000000000
        self.peer_id = self.clear_query['message']['peer_id']
        self.message = self.clear_query['message']
        self.text = self.clear_query['message']['text']
        self.lower = self.text.lower()
        self.payload = self.clear_query['message'].get("payload")
        self.conversation_message_id = self.clear_query["message"]["conversation_message_id"]
        if self.peer_id == self.from_id:
            self.send_id = {"user_id": self.chat_id}
            return
        self.send_id = {"chat_id": self.chat_id}


class LogJournal:
    def insert_new_error_line(self, line):
        with open(os.getcwd() + "\\vk_dark_errors.log", "a", encoding="UTF-8") as file:
            file.write(line)

    def insert_new_log_line(self, line):
        with open(os.getcwd() + "\\vk_dark_access.log", "a", encoding="UTF-8") as file:
            file.write(line)


class VKLongPoll:
    def __init__(self):
        print(f"{VKcolors.HEAD}Longpoll version {LONGPOLL_VERSION}{VKcolors.END}\n")
        self._ts = []
        if config["token"] is None:
            raise Exception("Config not loaded")
        self._lpserver = self.__update_server()
        if self._lpserver.get("error") is not None:
            raise LongpollConnectionError("The group_id or token is specified incorrectly in config.")
        self._url = None
        self._key = self._lpserver["response"]["key"]
        self._server = self._lpserver["response"]["server"]
        self._error = None
        self._session = requests.Session()
        self._ts.append(self._lpserver["response"]["ts"])

    def __update_server(self):
        payload = {
            'v': v,
            'group_id': config["group"],
            'access_token': config["token"]
        }
        return requests.get(url=vk_api_url + "groups.getLongPollServer", params=payload).json()

    def __one_listen(self):
        response = self._lpserver
        response_data = response['response']
        if len(self._ts) == 0:
            self._ts.append(response_data['ts'])
        payload = {
            'act': 'a_check',
            'key': str(self._key),
            'wait': '5',
            'ts': str(self._ts[0])
        }
        update_data = requests.post(url=self._server, data=payload)
        if update_data.json().get("failed") is not None:
            error = update_data.json()["failed"]
            updated_data = self.__update_server()
            if error == 2:
                self._key = updated_data["response"]["key"]
            return update_data
        self._ts = [update_data.json()['ts']]
        return update_data

    def listen(self):
        while True:
            call = self.__one_listen().json()
            if call.get("failed") is None:
                for information in call["updates"]:
                    if not config["debug"]:
                        yield EventInformation(information)
                    else:
                        debug_info = information["object"]["message"]
                        send_text = f"[{debug_info['peer_id']}] {debug_info['from_id']}: "
                        if debug_info["peer_id"] == debug_info["from_id"]:
                            send_text = f"{debug_info['from_id']}: "
                        date = datetime.datetime.now().strftime('%b %d, %Y %H:%M:%S')
                        print(f'[{date}] {VKcolors.HEAD}{send_text}{VKcolors.OKBLUE}{debug_info["text"]}{VKcolors.END}')
                        LogJournal().insert_new_log_line(f"[{date}] {send_text} {debug_info['text']}\n")
                        yield EventInformation(information)


class GetApi:
    __slots__ = ['_method', '__api_token', '__v']

    def __init__(self, method=None):
        if config["token"] is None:
            raise Exception("Config not loaded")
        self.__api_token = config["token"]
        self.__v = "5.130"
        self._method = method

    def __getattr__(self, method):
        if self._method is None:
            return GetApi(method=f"{method}")
        return GetApi(method=f"{self._method}.{method}")

    def __call__(self, **kwargs):
        """
        :param method: Метод выполняемый в вк апи
        :param kwargs: Аргументы для этого метода
        :return: https://vk.com/dev/methods
        """
        success = f"{VKcolors.OKGREEN}успешно"
        if self._method is None:
            self.__return_traceback('Method not entered')
        kwargs.update({"v": self.__v, "access_token": self.__api_token})
        rw = requests.get(vk_api_url + self._method, params=kwargs)
        if rw.json().get('error'):
            text_s = rw.json()["error"]["error_msg"]
            self.__return_traceback(text_s)
            success = f"{VKcolors.FAIL}ошибкой"
        date = datetime.datetime.now().strftime('%b %d, %Y %H:%M:%S')
        LogJournal().insert_new_log_line(f"[{date}] Вызван  метод {self._method}\n")
        print(f"Выполнение запроса '{self._method}' закончилось {success}. {VKcolors.END}\n")
        return rw.json()

    def __return_traceback(self, text_s):
        date = datetime.datetime.now().strftime('%b %d, %Y %H:%M:%S')
        if config["debug"]:
            print(f"[{date}] {VKcolors.FAIL}[ERR] {VKcolors.OKCYAN}{text_s}{VKcolors.END}")
            LogJournal().insert_new_error_line(f"[{date}] {text_s}\n")
            return
        raise ApiMethodError(text_s)
