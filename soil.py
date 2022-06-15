import adafruit_mcp3xxx.mcp3008 as mcp
import board
import busio
import digitalio

from adafruit_mcp3xxx.analog_in import AnalogIn

_channel = AnalogIn(mcp.MCP3008(busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI),
                                digitalio.DigitalInOut(board.CE0)), mcp.P0)


def moisture(moist: float, dry: float) -> float:
    if moist == dry:    # Avoids division by zero.
        return float('nan')

    percentage = 100 - (voltage() - moist) / (dry - moist) * 100    # Converts the voltage to a percentage based on the configured threshold values.

    return round(max(0.0, min(percentage, 1.0)), 2)


def voltage():
    return round(_channel.voltage, 2)
