#!/usr/bin/env python3

import sys
from configparser import ConfigParser
from logger import Logger, CONFIG_PATH


__config: ConfigParser
__instance: Logger


def main(args):
    global __config
    global __instance

    try:
        __config = ConfigParser()
        __config.optionxform = str
        __config.read_dict({'Logging': {
            'HubUrl': 'http://192.168.137.1:5191/hubs/logger',
            'RestUrl': 'localhost',
            'Moist': 1.2,
            'Dry': 3.3
        }})

        __config.read(CONFIG_PATH)

        __instance = Logger(__config)
        __instance.connect()
    finally:
        if __instance is not None:
            __instance.cleanup()

        if __config is not None:
            with open(CONFIG_PATH, 'w') as c:
                __config.write(c)


if __name__ == '__main__':
    main(sys.argv)
