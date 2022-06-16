import adafruit_mcp3xxx.mcp3008 as mcp
import board
import busio
import digitalio

from adafruit_mcp3xxx.analog_in import AnalogIn

_channel = AnalogIn(mcp.MCP3008(busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI),
                                digitalio.DigitalInOut(board.CE0)), mcp.P0)


def moisture(moist: float, dry: float) -> float:
    """
    Measures the soil moisture as a percentage based on the voltage from the ADC pin.

    The equation for calculating the percentage is as follows: M{100 - (voltage - moist) / (dry - moist)}.

    Returns M{NaN} if the threshold values are equal to each other to avoid division by zero.

    @param moist: Threshold value for moist soil.
    @param dry: Threshold value for dry soil.
    @return: The soil moisture as a percentage between M{0.0} and M{100.0}.
    """

    if moist == dry:    # Avoids division by zero.
        return float('nan')

    percentage = 100 - (voltage() - moist) / (dry - moist) * 100  # Converts the voltage to a percentage based on the configured threshold values.

    return round(max(0.0, min(percentage, 1.0)), 2)


def voltage() -> float:
    return round(_channel.voltage, 2)
