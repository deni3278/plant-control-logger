#!/usr/bin/env python3

import sys
from configparser import ConfigParser

import logger


def main(args):
    try:
        config = ConfigParser()
        config.optionxform = str
        config.read_dict({'Logging': {
            'HubUrl': 'localhost',
            'Moist': 1.2,
            'Dry': 3.3
        }})

        config.read(logger.CONFIG_PATH)

        instance = logger.Logger(config)
        instance.connect()
    finally:
        instance.led.cleanup()


if __name__ == '__main__':
    main(sys.argv)
