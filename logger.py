import logging
from configparser import ConfigParser
from air import Air
from led import Led
from soil import Soil
from gpiozero import Button
from signal import pause
from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.hub_connection_builder import HubConnectionBuilder

CONFIG_PATH = './config.ini'


class Logger:
    __BUTTON_PIN: int = 19

    def __init__(self, config: ConfigParser):
        self.__config = config
        self.__air = Air()
        self.__soil = Soil()
        self.__led = Led()
        self.__button = Button(self.__BUTTON_PIN)
        self.__button.when_activated = lambda: self.log()
        self.__soil.moist = float(config['Logging']['Moist'])
        self.__soil.dry = float(config['Logging']['Dry'])

        self.__hub_connection: BaseHubConnection = HubConnectionBuilder() \
            .with_url(config['Logging']['HubUrl']) \
            .configure_logging(logging.DEBUG) \
            .build()

    def connect(self):
        status = False

        try:
            status = self.__hub_connection.start()
        except Exception as e:
            print(e)

        if status:
            self.__led.blink_green()
        else:
            self.__led.blink_red()

        pause()

    def log(self):
        print('\n' + str(self.__air.temperature) + ' C')
        print(str(self.__air.humidity) + ' %')

        voltage = self.__soil.voltage

        print(str(round(voltage, 2)) + ' V')
        print(str(round(self.__soil.normalize(voltage), 2)) + ' %')

    def cleanup(self):
        """Releases GPIO ports."""
        self.__led.cleanup()
        self.__button.close()
