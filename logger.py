import time
from configparser import ConfigParser
from logging import DEBUG

from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.hub_connection_builder import HubConnectionBuilder

from air import Air
from led import Led
from soil import Soil

CONFIG_PATH = 'config.ini'


class Logger:
    def __init__(self, config: ConfigParser):
        self.config = config
        self.air = Air()
        self.soil = Soil()
        self.led = Led()
        self.connection: BaseHubConnection = HubConnectionBuilder() \
            .with_url('http://192.168.137.1:5140/hubs/logger') \
            .configure_logging(DEBUG) \
            .build()

        self.soil.moist = float(config['Logging']['Moist'])
        self.soil.dry = float(config['Logging']['Dry'])

    def connect(self):
        connected = self.connection.start()

        if connected:
            self.led.toggle_green(True)
        else:
            self.led.toggle_green(False)

        while True:
            self.log()
            time.sleep(5)

    def log(self):
        print('\n' + str(self.air.temperature) + ' C')
        print(str(self.air.humidity) + ' %')

        voltage = self.soil.voltage

        print(str(round(voltage, 2)) + ' V')
        print(str(round(self.soil.normalize(voltage), 2)) + ' %')
