#!/usr/bin/env python3
import asyncio
import sys
from configparser import ConfigParser

from logger import Logger, CONFIG_PATH

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
                'HubUrl': 'ws://40.87.132.220:9093/hubs/logger',
                'RestUrl': 'http://40.87.132.220:9092'
            },
            'Air': {
                'MinHumid': 0,
                'MaxHumid': 0,
                'MinTemp': 0,
                'MaxTemp': 0
            },
            'Soil': {
                'Moist': 0,
                'Dry': 0
            }})

        __config.read(CONFIG_PATH)

        if __config['Logging']['LoggerId'] == '':
            print('Logger has not been set up with an id yet.')
            exit()

        with Logger(__config) as __instance:
            __instance.connect()
    finally:
        with open(CONFIG_PATH, 'w') as c:
            __config.write(c)


if __name__ == '__main__':
    asyncio.run(main(sys.argv))
