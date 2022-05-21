import adafruit_am2320
import board
import busio


class Air:
    def __init__(self):
        self.sensor = adafruit_am2320.AM2320(busio.I2C(board.SCL, board.SDA))

    @property
    def humidity(self) -> float:
        return self.sensor.relative_humidity

    @property
    def temperature(self) -> float:
        return self.sensor.temperature
