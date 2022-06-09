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


def read(config: ConfigParser) -> dict:
    return {
        'Logging': {
            'LoggerId': config.get('Logging', 'LoggerId'),
            'PairingId': config.get('Logging', 'PairingId'),
            'Active': config.getboolean('Logging', 'Active'),
            'SocketUrl': config.get('Logging', 'SocketUrl'),
            'RestUrl': config.get('Logging', 'RestUrl')
        },
        'Air': {
            'MinHumid': config.getfloat('Air', 'MinHumid'),
            'MaxHumid': config.getfloat('Air', 'MaxHumid'),
            'MinTemp': config.getfloat('Air', 'MinTemp'),
            'MaxTemp': config.getfloat('Air', 'MaxTemp')
        },
        'Soil': {
            'Moist': config.getfloat('Soil', 'Moist'),
            'Dry': config.getfloat('Soil', 'Dry')
        }
    }


def save(config: ConfigParser, path: str):
    with open(path, 'w') as c:
        config.write(c)


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
            .with_url('ws://' + self.__config.get('Logging', 'SocketUrl') + '/hubs/logger') \
            .configure_logging(logging.DEBUG) \
            .build()

        self.__hub_connection.on('GetConfig', lambda message: util.send(self.__hub_connection, 'SendConfig', [
            {s: dict(self.__config.items(s)) for s in self.__config.sections()}]))

        self.__hub_connection.on('SetConfig', lambda new: config.read_dict(new))

    def __enter__(self):
        return self

    def connect(self):
        def on_open():
            util.send(self.__hub_connection, 'ConnectLogger', ['test'],
                      lambda result: self.__start_timer() if result else exit(), lambda: self.__led.blink_red())

            util.send(self.__hub_connection, 'SendConfig', [read(self.__config)])

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
        print(str(self.__air.temperature) + ' C')
        print(str(self.__air.humidity) + ' %')

        voltage = self.__soil.voltage

        print(str(round(voltage, 2)) + ' V')
        print(str(round(self.__soil.normalize(voltage), 2)) + ' %')

    def __start_timer(self):
        self.__led.blink_green()
        timer = threading.Timer(10, self.__tick)
        timer.start()

    def __tick(self):
        if self.__config.getboolean('Logging', 'Active'):
            self.__led.stop_red()
            self.__led.set_green(1)
            self.log()
        else:
            self.__led.stop_green()
            self.__led.set_red(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Releases GPIO ports."""
        self.__led.cleanup()
        self.__button.close()
