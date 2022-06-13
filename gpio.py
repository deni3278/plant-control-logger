from gpiozero import PWMLED


class GPIO:
    __GREEN = 26
    __RED = 21

    def __init__(self):
        print('Initializing GPIOs')

        self.__green = PWMLED(self.__GREEN)
        self.__red = PWMLED(self.__RED)

    def set_green(self, value: float):
        self.__green.value = max(0.0, min(value, 1.0))
        self.__red.value = 0.0

    def set_red(self, value: float):
        self.__red.value = max(0.0, min(value, 1.0))
        self.__green.value = 0.0

    def blink_green(self, interval: float = 0.5):
        self.__green.blink(interval, interval, 0, 0)
        self.__red.value = 0.0

    def blink_red(self, interval: float = 0.5):
        self.__red.blink(interval, interval, 0, 0)
        self.__green.value = 0.0

    def close(self):
        self.__green.close()
        self.__red.close()
