import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as mcp
from adafruit_mcp3xxx.analog_in import AnalogIn
import board


class Hydro:
    spi: busio.SPI
    cs: digitalio.DigitalInOut
    mcp: mcp.MCP3008
    chan: AnalogIn

    def setup(self):
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self.cs = digitalio.DigitalInOut(board.CE0)
        self.mcp = mcp.MCP3008(self.spi, self.cs)
        self.chan = AnalogIn(self.mcp, mcp.P0)

    def measure(self) -> float:
        return self.chan.voltage
