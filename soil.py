import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as mcp
from adafruit_mcp3xxx.analog_in import AnalogIn
import board

water = 0.88
air = 3.3


class Soil:
    spi: busio.SPI
    cs: digitalio.DigitalInOut
    mcp: mcp.MCP3008
    chan: AnalogIn

    def __init__(self):
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self.cs = digitalio.DigitalInOut(board.CE0)
        self.mcp = mcp.MCP3008(self.spi, self.cs)
        self.chan = AnalogIn(self.mcp, mcp.P0)

    def measure_voltage(self) -> float:
        return self.chan.voltage

    def measure_value(self) -> int:
        return self.chan.value

    @staticmethod
    def normalize(voltage: float):
        value = 100 - (voltage - water) / (air - water) * 100
        value = 0 if value < 1 else value
        value = 100 if value > 99 else value

        return value
