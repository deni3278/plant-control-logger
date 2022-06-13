from gpiozero import PWMLED


class Led:
    __RED_PIN = 21
    __GREEN_PIN = 26

    def __init__(self):
        self.__red_led = PWMLED(self.__RED_PIN)
        self.__green_led = PWMLED(self.__GREEN_PIN)

    def set_red(self, value: float):
        """Sets the brightness of the red LED as a value between 0 and 1."""
        self.__red_led.value = value

    def blink_red(self):
        """Starts blinking the red LED switching every half second."""
        self.__red_led.blink(0.5, 0.5, 0, 0)

    def stop_red(self):
        """Stops blinking the red LED and sets the brightness to 0."""
        self.__red_led.off()

    def set_green(self, value: float):
        """Sets the brightness of the green LED as a value between 0 and 1."""
        self.__green_led.value = value

    def blink_green(self):
        """Starts blinking the green LED switching every half second."""
        self.__green_led.blink(0.5, 0.5, 0, 0)

    def stop_green(self):
        """Stops blinking the green LED and sets the brightness to 0."""
        self.__green_led.off()

    def cleanup(self):
        """Releases GPIO ports used by the LEDs."""
        self.__red_led.close()
        self.__green_led.close()

    @property
    def red_value(self):
        return self.__red_led.value

    @property
    def green_value(self):
        return self.__green_led.value
