import atexit
import logging

from gpiozero import PWMLED

_GREEN_PIN = 26
_RED_PIN = 21
_BLINK = 0.25

_green = PWMLED(_GREEN_PIN)
_red = PWMLED(_RED_PIN)


def set_green(value: float) -> None:
    """
    Sets the brightness of the green LED by using pulse-width modulation. The value is clamped between M{0.0}
    and M{1.0}.

    The red LED's brightness is set to M{0}.

    @param value: The brightness value.
    """

    _green.value = max(0.0, min(value, 1.0))
    _red.value = 0.0


def set_red(value: float) -> None:
    """
    Sets the brightness of the red LED by using pulse-width modulation. The value is clamped between M{0.0}
    and M{1.0}.

    The green LED's brightness is set to M{0}.

    @param value: The brightness value.
    """

    _red.value = max(0.0, min(value, 1.0))
    _green.value = 0.0


def blink_green(on_time: float = _BLINK, off_time: float = None) -> None:
    """
    Starts the green LED blinking and sets the brightness of the red LED to M{0}.

    @param on_time: Number of seconds that the green LED should be on.
    @param off_time: Number of seconds that the green LED should be on.
    """

    _green.blink(on_time, off_time or on_time, 0, 0)
    _red.value = 0.0


def blink_red(on_time: float = _BLINK, off_time: float = None) -> None:
    """
    Starts the red LED blinking and sets the brightness of the green LED to M{0}.

    @param on_time: Number of seconds that the red LED should be on.
    @param off_time: Number of seconds that the red LED should be on.
    """

    _red.blink(on_time, off_time or on_time, 0, 0)
    _green.value = 0.0


def cleanup() -> None:
    """
    Cleans up the used GPIOs.
    """

    logging.info('Cleaning up GPIOs.')

    _green.close()
    _red.close()


atexit.register(cleanup)  # Register the cleanup method as a handler for when the script is exiting.
