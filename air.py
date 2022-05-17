import busio
import board
import adafruit_am2320


class Air:
    sensor: adafruit_am2320.AM2320

    def setup(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_am2320.AM2320(i2c)

    def measure_humidity(self) -> float:
        return self.sensor.relative_humidity

    def measure_temp(self) -> float:
        return self.sensor.temperature
