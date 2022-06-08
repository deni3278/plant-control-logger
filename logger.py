import logging
import threading
from configparser import ConfigParser
from signal import pause

from gpiozero import Button
from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.hub_connection_builder import HubConnectionBuilder

import util
from air import Air
from led import Led
from soil import Soil

CONFIG_PATH = './config.ini'


class Logger:
    __BUTTON_PIN: int = 19

    def __init__(self, config: ConfigParser):
        self.__config = config

        self.__air = Air()
        self.__soil = Soil(config)
        self.__led = Led()

        self.__button = Button(self.__BUTTON_PIN)
        self.__button.when_activated = lambda: self.log()

        self.__hub_connection: BaseHubConnection = HubConnectionBuilder() \
            .with_url('ws://192.168.137.1:5140/hubs/logger') \
            .configure_logging(logging.DEBUG) \
            .build()

        self.__hub_connection.on('GetConfig', lambda: self.__hub_connection.send("SendConfig", [
            {s: dict(config.items(s)) for s in config.sections()}]))

        self.__hub_connection.on('SetConfig', lambda new: config.read_dict(new))

    def __enter__(self):
        return self

    def connect(self):
        def on_open():
            util.send(self.__hub_connection, 'ConnectLogger', ['test'], lambda result: self.__start_timer(), lambda: self.__led.blink_red())

        def on_error():
            self.__led.blink_red()

        try:
            self.__hub_connection.start()
            self.__hub_connection.on_open(on_open)
            self.__hub_connection.on_error(on_error)
        except Exception as e:
            print(e)

        pause()

    def log(self):
        print('\n' + str(self.__air.temperature) + ' C')
        print(str(self.__air.humidity) + ' %')

        voltage = self.__soil.voltage

        print(str(round(voltage, 2)) + ' V')
        print(str(round(self.__soil.normalize(voltage), 2)) + ' %')

    def __start_timer(self):
        self.__led.blink_green()
        timer = threading.Timer(10, self.log)
        timer.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Releases GPIO ports."""
        self.__led.cleanup()
        self.__button.close()
