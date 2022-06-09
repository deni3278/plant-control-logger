#!/usr/bin/env python3
import asyncio
import sys
from configparser import ConfigParser

import requests

from logger import Logger, CONFIG_PATH

default_config = {
    'Logging': {
        'LoggerId': '',
        'PairingId': '',
        'Active': False,
        'SocketUrl': '40.87.132.220:9093',
        'RestUrl': '40.87.132.220:9092'
    },
    'Air': {
        'MinHumid': 1,
        'MaxHumid': 1,
        'MinTemp': 1,
        'MaxTemp': 1
    },
    'Soil': {
        'Moist': 1.2,
        'Dry': 3.3
    }}

__config: ConfigParser


async def main(args):
    global __config

    try:
        __config = ConfigParser()
        __config.optionxform = str
        __config.read_dict({
            'Logging': {
                'LoggerId': '',
                'PairingId': '',
                'Active': False,
                'SocketUrl': '40.87.132.220:9093',
                'RestUrl': '40.87.132.220:9092'
            },
            'Air': {
                'MinHumid': 1,
                'MaxHumid': 1,
                'MinTemp': 1,
                'MaxTemp': 1
            },
            'Soil': {
                'Moist': 1.2,
                'Dry': 3.3
            }})

        __config.read(CONFIG_PATH)

        if __config.get('Logging', 'LoggerId') == '':
            print('Logger has not been set up with an id yet.')
            exit()

        check_connection()

        with Logger(__config) as __instance:
            __instance.connect()
    finally:
        with open(CONFIG_PATH, 'w') as c:
            __config.write(c)


def check_connection():
    connection: bool = False
    url: str = 'http://' + __config.get('Logging', 'SocketUrl') + '/'

    print('Attempting to connect to backend.')

    while not connection:
        try:
            requests.get(url, timeout=10)
            connection = True
        except (requests.ConnectionError, requests.Timeout):
            print('Retrying connection to backend.')


if __name__ == '__main__':
    asyncio.run(main(sys.argv))
