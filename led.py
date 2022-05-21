import RPi.GPIO as GPIO


class Led:
    __RED = 21
    __GREEN = 26

    def __init__(self):
        self.__red = False
        self.__green = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__RED, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.__GREEN, GPIO.OUT, initial=GPIO.LOW)

    def toggle_red(self, state: bool):
        signal = GPIO.LOW if not state else GPIO.HIGH
        GPIO.output(self.__RED, signal)
        self.__red = state

    def toggle_green(self, state: bool):
        signal = GPIO.LOW if not state else GPIO.HIGH
        GPIO.output(self.__GREEN, signal)
        self.__green = state

    def cleanup(self):
        GPIO.cleanup([self.__RED, self.__GREEN])

    @property
    def red(self):
        return self.__red

    @property
    def green(self):
        return self.__green
