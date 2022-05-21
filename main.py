from air import Air
from led import Led
from soil import Soil
import logging
from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.hub_connection_builder import HubConnectionBuilder

red_pin = 21
green_pin = 26

air = Air()
soil = Soil()
led = Led(red_pin, green_pin)

hub_connection: BaseHubConnection = HubConnectionBuilder() \
    .with_url('http://192.168.137.1:5140/hubs/logger') \
    .configure_logging(logging.DEBUG) \
    .build()


def log():
    print(str(air.measure_temp()) + ' C')
    print(str(air.measure_humidity()) + ' %')
    print(str(round(soil.measure_voltage(), 2)) + ' V')
    print(str(round(soil.normalize(soil.measure_voltage()), 2)) + ' %')


try:
    hub_connection.start()
    log()
finally:
    led.cleanup()
    hub_connection.stop()
