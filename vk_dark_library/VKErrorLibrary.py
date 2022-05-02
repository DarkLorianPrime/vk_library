class BaseException(Exception):
    def __init__(self, *args):
        if args:
            self.error = args[0]
            return
        self.error = "Critical error!"

    def __str__(self):
        return self.error


class LongpollConnectionError(BaseException):
    pass


class ApiMethodError(BaseException):
    pass
