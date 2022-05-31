import adafruit_am2320
import board
import busio


class Air:
    """Measures air humidity and temperature."""

    def __init__(self):
        self.sensor = adafruit_am2320.AM2320(busio.I2C(board.SCL, board.SDA))

    @property
    def humidity(self) -> float:
        """The measured relative humidity in percent."""
        return self.sensor.relative_humidity

    @property
    def temperature(self) -> float:
        """The measure air temperature in celsius."""
        return self.sensor.temperature
