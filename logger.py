import sys
from configparser import ConfigParser
from threading import Timer

import requests
from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.hub_connection_builder import HubConnectionBuilder

from am2320 import AM2320
from config import to_dict, PATH
from gpio import GPIO
from mcp3008 import MCP3008


class Logger:
    __BLINK = 0.1
    __INTERVAL = 60

    def __init__(self, config: ConfigParser):
        """
        Initializes a logger instance by setting up sensors, GPIOs, and backend connections.

        Sets up the hub connection and registers hub method handlers.

        Parameters
        ----------
        config : ConfigParser
            Settings to use for initialization
        """
        self.__config = config

        self.__am2320 = AM2320()
        self.__mcp3008 = MCP3008()
        self.__gpio = GPIO()

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
        self.__connection.on('SetPairingId', lambda args: self.__on_set_pairing_id(args[0]))
        self.__connection.on('Calibrate', lambda args: self.__on_calibrate(args[0]))
        self.__connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Cleaning up resources')

        self.__gpio.close()

    def __log(self):
        print('Logging')

        pairing_id = self.__config.get('Logging', 'PairingId')
        temp = str(self.__am2320.temperature)
        humidity = self.__am2320.humidity
        moisture = round(self.__mcp3008.moisture(self.__config), 2)

        rest: str = 'http://' + self.__config.get('Logging', 'RestUrl') + '/logs'

        try:
            response = requests.post(rest, json={
                "pairing": pairing_id,
                "temperature": temp,
                "humidity": humidity,
                "moisture": moisture
            })

            print(response.json())
        except requests.exceptions.Timeout:
            print('Timed out posting log')

            try:
                self.__timer.cancel()
                self.__ping()
                self.__tick()
            except AttributeError:
                pass
        except requests.exceptions.InvalidURL:
            sys.exit('Invalid URL from config.ini')

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
        """
        Handler for the ``Calibrate`` hub method.

        Measures the current voltage using the moisture sensor and sets the value in the ``config.ini`` file.
        The ``calibration_type`` determines which key to look for in ``config.ini``.

        Parameters
        ----------
        calibration_type : str
            Either Moist or Dry as a string.
        """
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
        """
        Handler for the ``GetConfig`` hub method.

        Sends the ``ConfigParser`` instance as a ``dict`` to the hub.
        """
        print('GetConfig')

        self.__connection.send('SendConfig', [to_dict(self.__config)])

    def __on_set_config(self, new: dict):
        """
        Handler for the ``GetConfig`` hub method.

        Updates the ``ConfigParser`` instance with the new settings and saves it to ``config.ini``.

        Parameters
        ----------
        new : dict
            Received config options as a dict.
        """
        print('SetConfig')

        self.__config.read_dict(new)
        self.__save()

        if self.__config.getboolean('Logging', 'Active'):
            self.__gpio.set_green(1.0)
        else:
            self.__gpio.set_red(1.0)

    def __on_set_pairing_id(self, pairing_id: str):
        """
        Handler for the ``SetPairingId`` hub method.

        Updates the ``ConfigParser`` instance with the new pairing id and saves it to ``config.ini``.

        Parameters
        ----------
        pairing_id : str
            The new pairing id.
        """
        print('SetPairingId')

        self.__config.set('Logging', 'PairingId', pairing_id)
        self.__save()

    def __on_open(self):
        """
        Handler for when the hub connection is opened.

        Sends a ``ConnectLogger`` message to the hub to authenticate and register itself as online to the frontends.
        If the authentication was successful, the main loop is started.
        """
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
        """
        Handler for when the hub connection is attempting reconnection.

        Cancels the main loop, if it's running, and attempts to reconnect.
        """
        print('Attempting to reconnect to backend')

        try:
            self.__timer.cancel()
            self.__ping()
            self.__tick()
        except AttributeError:
            pass

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

        self.__gpio.blink_green(self.__BLINK)

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
