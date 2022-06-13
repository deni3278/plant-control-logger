import sys
from threading import Timer
from configparser import ConfigParser

import requests
from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.hub_connection_builder import HubConnectionBuilder

from config import to_dict, PATH
from am2320 import AM2320
from gpio import GPIO
from mcp3008 import MCP3008


class Logger:
    __BLINK = 0.1
    __INTERVAL = 5

    def __init__(self, config: ConfigParser):
        self.__config = config

        self.__am2320 = AM2320()
        self.__mcp3008 = MCP3008()
        self.__gpio = GPIO()
        self.__gpio.blink_green(self.__BLINK)

        self.__ping()

        self.__connection: BaseHubConnection = HubConnectionBuilder() \
            .with_url('ws://' + self.__config.get('Logging', 'SocketUrl') + '/hubs/logger') \
            .with_automatic_reconnect({
                'type': 'raw',
                'keep_alive_interval': 10,
                'reconnect_interval': 5
            }).build()

        self.__connection.on_open(self.__on_open)
        self.__connection.on_reconnect(lambda: self.__gpio.blink_red(self.__BLINK))
        self.__connection.on_close(self.__on_close)
        self.__connection.on_error(lambda args: sys.exit(args.error))
        self.__connection.on('GetConfig', lambda args: self.__on_get_config())
        self.__connection.on('SetConfig', lambda args: self.__on_set_config(args[0]))
        self.__connection.on('Calibrate', lambda args: self.__on_calibrate(args[0]))
        self.__connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Cleaning up resources')

        self.__gpio.close()

    def __log(self):
        # Todo: POST to API

        print(str(self.__am2320.temperature) + ' C')
        print(str(self.__am2320.humidity) + ' %')
        print(str(round(self.__mcp3008.moisture(self.__config), 2)) + ' %')

    def __tick(self):
        print('Tick')

        if self.__config.getboolean('Logging', 'Active'):
            self.__gpio.set_green(1.0)
            self.__log()
        else:
            self.__gpio.set_red(1.0)

        self.__timer = Timer(self.__INTERVAL, self.__tick)
        self.__timer.start()

    def __on_calibrate(self, calibration_type: str):
        if calibration_type == 'Moist':
            print('Calibrating moist')

            self.__config.set('Soil', 'Moist', str(round(self.__mcp3008.voltage, 2)))
        elif calibration_type == 'Dry':
            print('Calibrating dry')

            self.__config.set('Soil', 'Dry', str(round(self.__mcp3008.voltage, 2)))
        else:
            return

        self.__save()

    def __on_get_config(self):
        print('GetConfig')

        self.__connection.send('SendConfig', [to_dict(self.__config)])

    def __on_set_config(self, new: dict):
        print('SetConfig')

        self.__config.read_dict(new)
        self.__save()

        if self.__config.getboolean('Logging', 'Active'):
            self.__gpio.set_green(1.0)
        else:
            self.__gpio.set_red(1.0)

    def __on_open(self):
        print('Authenticating')

        logger_id = self.__config.get('Logging', 'LoggerId')

        def callback(result):
            if result:
                print('Successfully connected to backend')

                self.__connection.send('SendConfig', [to_dict(self.__config)])
                self.__tick()
            else:
                sys.exit('A logger is already connected to the backend with the same ID')

        self.__connection.send('ConnectLogger', [logger_id], callback)

    def __on_reconnect(self):
        print('Attempting to reconnect to backend')

        try:
            self.__timer.cancel()
        except AttributeError:
            pass

        self.__gpio.blink_red(self.__BLINK)

    def __on_close(self):
        print('Connection closed to backend')

        try:
            self.__timer.cancel()
        except AttributeError:
            pass

        self.__connect()

    def __connect(self):
        print('Connecting to backend')

        self.__gpio.blink_green(self.__BLINK)
        self.__connection.start()

    def __save(self):
        print('Saving config')

        try:
            self.__connection.send('SendConfig', [to_dict(self.__config)])
        except AttributeError:
            pass

        with open(PATH, 'w') as f:
            self.__config.write(f)

    def __ping(self):
        connection: bool = False
        socket: str = 'http://' + self.__config.get('Logging', 'SocketUrl') + '/'
        rest: str = 'http://' + self.__config.get('Logging', 'RestUrl') + '/'

        print('Pinging backend servers')

        while not connection:
            try:
                requests.get(socket, timeout=5)
                requests.get(rest, timeout=5)

                connection = True
            except requests.Timeout as e:
                print(str(e))

                self.__gpio.blink_red(self.__BLINK)
            except requests.exceptions.InvalidURL:
                sys.exit('Invalid URL from config.ini')

        print('Pong')

        self.__gpio.blink_green(self.__BLINK)
