import datetime
import os
import multiprocessing

from vk_dark_library.VKUtils import VKcolors, DEBBUGER_VERSION

first_start = []
texts = {
    "start_dev": f"\nDebbuger version {DEBBUGER_VERSION}\n{VKcolors.FAIL}Используйте этот режим только для тестирования!",
    "restart_dev": f'\nБыли обнаружены изменения\nDebbuger version {DEBBUGER_VERSION}\nКод был перезагружен'
}
times = {}


class InitializeDebugger:
    def __init__(self, main_function):
        """

        :param main_function: your function that will be called
        """
        self.__main_function = main_function
        self.__total_size = 0
        self.__old_size = 0
        self.__main_thread = multiprocessing.Process(target=main_function)

    def __run(self, isfirst=False):
        if isfirst:
            date = datetime.datetime.now().strftime('%b %d, %Y %H:%M:%S')
            print(f"{VKcolors.HEAD}[{date}] - {texts['start_dev']}{VKcolors.END}")
        self.__main_thread.start()

    def __restart(self):
        date = datetime.datetime.now().strftime('%b %d, %Y %H:%M:%S')
        print(f"{VKcolors.HEAD}[{date}] - {texts['restart_dev']}{VKcolors.END}")
        self.__main_thread.terminate()
        self.__main_thread = multiprocessing.Process(target=self.__main_function, name="main_function")
        self.__run()

    def start_debug(self):
        while True:
            restructed = False
            for path, dirs, files in os.walk(os.getcwd()):
                for file in files:
                    f_j = os.path.join(path, file)
                    if f_j.endswith(".py"):
                        if times.get(f_j) != os.path.getmtime(f_j):
                            times[f_j] = os.path.getmtime(f_j)
                            restructed = True
            if not restructed:
                continue
            if not first_start:
                first_start.append(True)
                self.__run(isfirst=True)
                continue

            self.__restart()
