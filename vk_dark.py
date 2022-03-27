import importlib
import os
import sys

import requests

File_url = None
token = os.getenv("token")
group = os.getenv("group")
vk_api_url = "https://api.vk.com/method/"
v = '5.130'
data = {"v": "5.130", "token": None, "group": None}
NEW = "message_new"


class load_config:
    def __init__(self, path, name):
        if path is not None:
            sys.path.append(path)
            config = importlib.import_module(name)
            data.update({"token": config.token, "group": config.group_id})


class EventInformation:
    __slots__ = ["clear_query", "group_id", "chat_id", "message", "type", "text", "from_id", "peer_id"]

    def __init__(self, raw_query):
        if data["token"] is None:
            raise Exception("Config not loaded")
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


def update_server():
    payload = {
        'v': v,
        'group_id': data["group"],
        'access_token': data["token"]
    }
    print("update_server")
    return requests.get(url=vk_api_url + "groups.getLongPollServer", params=payload).json()


class Main:
    def __init__(self):
        self.ts = []
        if data["token"] is None:
            raise Exception("Config not loaded")
        self.lpserver = update_server()
        self.url = None
        self.key = self.lpserver["response"]["key"]
        self.server = self.lpserver["response"]["server"]
        self.error = None
        self.session = requests.Session()
        self.ts.append(self.lpserver["response"]["ts"])

    def one_listen(self):
        response = self.lpserver
        response_data = response['response']
        if len(self.ts) == 0:
            self.ts.append(response_data['ts'])
        self.key = response_data['key']
        self.server = response_data['server']
        payload = {
            'act': 'a_check',
            'key': str(self.key),
            'wait': '5',
            'ts': str(self.ts[0])
        }
        update_data = requests.post(url=self.server, data=payload)
        if update_data.json().get("error") is not None:
            error = update_data.json()["error"]
            updated_data = update_server()
            print(error)
            if error == 2:
                self.key = updated_data["response"]["key"]
            return update_data
        print(update_data.json())
        self.ts = [update_data.json()['ts']]
        return update_data

    def listen(self):
        while True:
            call = self.one_listen().json()
            if call.get("error") is None:
                for information in call["updates"]:
                    yield EventInformation(information)


class get_api(object):
    __slots__ = ['_method', 'api_token', 'v']

    def __init__(self, method=None):
        if data["token"] is None:
            raise Exception("Config not loaded")
        self.api_token = data["token"]
        self.v = "5.130"
        self._method = method

    def __getattr__(self, method):
        if self._method is None:
            return get_api(method=f"{method}")
        return get_api(method=f"{self._method}.{method}")

    def __call__(self, **kwargs):
        """
        :param method: Метод выполняемый в вк апи
        :param kwargs: Аргументы для этого метода
        :return: https://vk.com/dev/methods
        """
        if self._method is None:
            self.return_traceback('Method not entered')
        kwargs.update({"v": self.v, "access_token": self.api_token})
        rw = requests.get(vk_api_url + self._method, params=kwargs)
        if rw.json().get('error'):
            text_s = rw.json()["error"]["error_msg"]
            self.return_traceback(text_s)
        return rw.json()

    def return_traceback(self, text_s):
        print(text_s)
        pass
        # raise Exceptions.MethodError(text_s)


def user_or_chat(vk_object: EventInformation) -> dict:
    """
    :param vk_object: функция, с которой можно взять айди чата и айди пользователя.
    :return: словарь, который можно сразу отправить в вк.
    """
    if vk_object.peer_id == vk_object.from_id:
        return {"user_id": vk_object.chat_id}
    return {"chat_id": vk_object.chat_id}