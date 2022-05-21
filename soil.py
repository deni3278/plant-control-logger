import adafruit_mcp3xxx.mcp3008 as mcp
import board
import busio
import digitalio
from adafruit_mcp3xxx.analog_in import AnalogIn


class Soil:
    def __init__(self):
        self.__moist = 0
        self.__dry = 0
        self.__chan = AnalogIn(mcp.MCP3008(busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI),
                                           digitalio.DigitalInOut(board.CE0)), mcp.P0)

    def normalize(self, voltage: float) -> float:
        return 100 - (voltage - self.__moist) / (self.__dry - self.__moist) * 100

    @property
    def voltage(self) -> float:
        return self.__chan.voltage

    @property
    def value(self) -> int:
        return self.__chan.value

    @property
    def moist(self):
        return self.__moist

    @moist.setter
    def moist(self, value):
        self.__moist = value

    @property
    def dry(self):
        return self.__dry

    @dry.setter
    def dry(self, value):
        self.__dry = value
