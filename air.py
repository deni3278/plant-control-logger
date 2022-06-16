import adafruit_am2320
import board
import busio

_sensor = adafruit_am2320.AM2320(busio.I2C(board.SCL, board.SDA))


def humidity() -> float:
    """
    Measures the relative air humidity.

    @return: The relative air humidity.
    """

    return round(_sensor.relative_humidity, 2)


def temperature() -> float:
    """
    Measures the air temperature.

    @return: The air temperature.
    """

    return round(_sensor.temperature, 2)
