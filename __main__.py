import logging
import os
import signal
import sys
import threading
from math import isnan

import requests
from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.hub_connection_builder import HubConnectionBuilder
from signalrcore.messages.completion_message import CompletionMessage

import air
import led
import soil
from config import Config

logging.basicConfig(level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S', format='%(asctime)s - %(levelname)s: %(message)s')

_INTERVAL = 10  # Number of seconds between iterations in the main loop.

_config = Config()

if len(_config.get('Logging', 'LoggerId')) == 0:
    sys.exit('Logger has not been registered with an ID.')

# noinspection PyTypeChecker
_timer: threading.Timer = None  # Globally defined for use in several functions.

_connection: BaseHubConnection = HubConnectionBuilder() \
    .with_url(os.path.join('ws://', _config.get('Logging', 'SocketUrl'), 'hubs', 'logger')) \
    .build()


def _log():
    logging.info('Logging.')

    pairing_id: str = _config.get('Logging', 'PairingId')
    temperature: float = air.temperature()
    humidity: float = air.humidity()
    moisture: float = soil.moisture(_config.getfloat('Soil', 'Moist'), _config.getfloat('Soil', 'Dry'))
    url: str = os.path.join('http://', _config.get('Logging', 'RestUrl'), 'logs')

    if isnan(moisture):
        logging.warning('Moist and dry threshold values must be different from each other.')    # Avoids division by zero.

        return

    try:
        response = requests.post(url, json={
            "pairing": pairing_id,
            "temperature": temperature,
            "humidity": humidity,
            "moisture": moisture
        })

        logging.info(response.json())
    except requests.Timeout:
        logging.warning('Timed out trying to communicate with \'{0}\'.'.format(url))

        led.blink_red()

        if _timer and _timer.is_alive():
            _timer.cancel()     # Stop the main loop to avoid multiple threads pinging at the same time.

        _ping(url)

        if _timer:      # Only if the main loop has been started previously.
            _on_tick()  # Resume the main loop after a response is received.


def _ping(url: str):
    logging.info('Pinging \'{0}\'.'.format(url))

    connection: bool = False

    while not connection:
        try:
            requests.get(url, timeout=5)

            connection = True
        except requests.Timeout:
            logging.warning('Timed out trying to communicate with \'{0}\'.'.format(url))

            connection = False
        except requests.ConnectionError:
            logging.critical('Cannot communicate with \'{0}\'.'.format(url))

            sys.exit()

        led.blink_green() if connection else led.blink_red()


def _on_open():
    logging.info('Opened connection to hub.')

    def on_response(message: CompletionMessage):
        if message.result:
            logging.info('Successfully authenticated.')

            _on_tick()  # Start main loop.
        else:
            logging.critical('A logger is already connected with the same ID')

            sys.exit()

    _connection.send('ConnectLogger', [_config.get('Logging', 'LoggerId')], on_response)    # Authenticate to the SignalR hub.


def _on_close():
    logging.warning('Connection to hub has been closed.')


def _on_error(message: CompletionMessage):
    logging.error(message.error)


def _on_get_config():
    logging.info('Received a \'GetConfig\' message.')

    _connection.send('SendConfig', [_config.to_dict()])


def _on_set_config(new: dict):
    logging.info('Received a \'SetConfig\' message.')

    _config.read_dict(new)
    _config.save()

    if _timer and _timer.is_alive():
        if _config.getboolean('Logging', 'Active'):
            led.set_green(1)
        else:
            led.set_red(1)


def _on_set_pairing_id(new: str):
    logging.info('Received a \'SetPairingId\' message.')

    _config.set('Logging', 'PairingId', new)
    _config.save()


def _on_calibrate(option: str):
    logging.info('Received a \'Calibrate\' message.')

    if option == 'Moist':
        logging.info('Calibrating moist soil threshold.')

        _config.set('Soil', 'Moist', soil.voltage())
    elif option == 'Dry':
        logging.info('Calibrating dry soil threshold.')

        _config.set('Soil', 'Dry', soil.voltage())
    else:
        return

    _config.save()


def _on_tick():
    global _timer

    logging.info('Tick.')

    if _config.getboolean('Logging', 'Active'):
        led.set_green(1)

        if len(_config.get('Logging', 'PairingId')) > 0:    # Only log if the logger has been paired with a plant.
            _log()
        else:
            logging.warning('Logger is not paired.')
    else:
        led.set_red(1)

    _timer = threading.Timer(_INTERVAL, _on_tick)   # Calls the same function, _on_tick, causing a loop.
    _timer.start()


_connection.on_open(_on_open)
_connection.on_close(_on_close)
_connection.on_error(_on_error)
_connection.on('GetConfig', lambda args: _on_get_config())
_connection.on('SetConfig', lambda args: _on_set_config(args[0]))
_connection.on('SetPairingId', lambda args: _on_set_pairing_id(args[0]))
_connection.on('Calibrate', lambda args: _on_calibrate(args[0]))

try:
    led.blink_green()

    _ping(os.path.join('http://', _config.get('Logging', 'RestUrl')))
    _ping(os.path.join('http://', _config.get('Logging', 'SocketUrl')))

    logging.info('Connecting to hub.')

    _connection.start()

    signal.pause()  # Unix only function that causes the process to sleep and, in this case, keeping the script alive.
except KeyboardInterrupt:
    sys.exit()
