from configparser import ConfigParser

import adafruit_mcp3xxx.mcp3008 as mcp
import board
import busio
import digitalio
from adafruit_mcp3xxx.analog_in import AnalogIn


class MCP3008:
    def __init__(self, config: ConfigParser):
        self.__config = config
        self.__chan = AnalogIn(mcp.MCP3008(busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI),
                                           digitalio.DigitalInOut(board.CE0)), mcp.P0)

    @property
    def moisture(self) -> float:
        moist = float(self.__config['Soil']['Moist'])
        dry = float(self.__config['Soil']['Dry'])

        return 100.0 - (self.__chan.voltage - moist) / (dry - moist) * 100.0
