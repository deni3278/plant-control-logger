import atexit
import logging

from gpiozero import PWMLED

_GREEN_PIN = 26
_RED_PIN = 21
_BLINK = 0.25

_green = PWMLED(_GREEN_PIN)
_red = PWMLED(_RED_PIN)


def set_green(value: float):
    _green.value = max(0.0, min(value, 1.0))
    _red.value = 0.0


def set_red(value: float):
    _red.value = max(0.0, min(value, 1.0))
    _green.value = 0.0


def blink_green(on_time: float = _BLINK, off_time: float = None):
    _green.blink(on_time, off_time or on_time, 0, 0)
    _red.value = 0.0


def blink_red(on_time: float = _BLINK, off_time: float = None):
    _red.blink(on_time, off_time or on_time, 0, 0)
    _green.value = 0.0


def cleanup():
    logging.info('Cleaning up GPIOs.')

    _green.close()
    _red.close()


atexit.register(cleanup)
