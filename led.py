from gpiozero import PWMLED


class Led:
    __RED_PIN = 21
    __GREEN_PIN = 26

    def __init__(self):
        self.__red_led = PWMLED(self.__RED_PIN)
        self.__green_led = PWMLED(self.__GREEN_PIN)

    def set_red(self, value: float):
        self.__red_led.value = value

    def blink_red(self):
        self.__red_led.blink(0.5, 0.5, 0, 0)

    def stop_red(self):
        self.__red_led.off()

    def set_green(self, value: float):
        self.__green_led.value = value

    def blink_green(self):
        self.__green_led.blink(0.5, 0.5, 0, 0)

    def stop_green(self):
        self.__green_led.off()

    def cleanup(self):
        self.__red_led.close()
        self.__green_led.close()

    @property
    def red_value(self):
        return self.__red_led.value

    @property
    def green_value(self):
        return self.__green_led.value
