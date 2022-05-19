import RPi.GPIO as GPIO


class Led:
    red: bool
    green: bool
    __red_pin: int
    __green_pin: int

    def __init__(self, red_pin, green_pin):
        self.__red_pin = red_pin
        self.__green_pin = green_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(red_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(green_pin, GPIO.OUT, initial=GPIO.LOW)

    def toggle_red(self):
        state = GPIO.LOW if GPIO.input(self.__red_pin) else GPIO.HIGH
        GPIO.output(self.__red_pin, state)
        self.red = state

    def toggle_green(self):
        state = GPIO.LOW if GPIO.input(self.__green_pin) else GPIO.HIGH
        GPIO.output(self.__green_pin, state)
        self.green = state

    def cleanup(self):
        GPIO.cleanup([self.__red_pin, self.__green_pin])
