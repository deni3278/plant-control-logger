import adafruit_mcp3xxx.mcp3008 as mcp
import board
import busio
import digitalio
from configparser import ConfigParser
from adafruit_mcp3xxx.analog_in import AnalogIn


class Soil:
    """Measures soil moisture."""

    def __init__(self, config: ConfigParser):
        self.__config = config
        self.__chan = AnalogIn(mcp.MCP3008(busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI),
                                           digitalio.DigitalInOut(board.CE0)), mcp.P0)

    def normalize(self, voltage: float) -> float:
        moist = float(self.__config['Soil']['Moist'])
        dry = float(self.__config['Soil']['Dry'])

        return 100 - (voltage - moist) / (dry - moist) * 100

    @property
    def voltage(self) -> float:
        """Voltage of the ADC pin as a floating point value."""
        return self.__chan.voltage

    @property
    def value(self) -> int:
        """Value of the ADC pin as an integer."""
        return self.__chan.value
