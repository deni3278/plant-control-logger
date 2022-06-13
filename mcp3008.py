from configparser import ConfigParser

import adafruit_mcp3xxx.mcp3008 as mcp
import board
import busio
import digitalio
from adafruit_mcp3xxx.analog_in import AnalogIn


class MCP3008:
    def __init__(self):
        print('Initializing MCP3008')

        self.__chan = AnalogIn(mcp.MCP3008(busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI),
                                           digitalio.DigitalInOut(board.CE0)), mcp.P0)

    def moisture(self, config: ConfigParser) -> float:
        moist = float(config['Soil']['Moist'])
        dry = float(config['Soil']['Dry'])

        if moist == dry:
            return float('nan')

        percentage = 100.0 - (self.__chan.voltage - moist) / (dry - moist) * 100.0

        return max(0.0, min(percentage, 1.0))

    @property
    def voltage(self):
        return self.__chan.voltage
