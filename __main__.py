#!/usr/bin/env python3

import os
from configparser import ConfigParser

import defaults
from am2320 import AM2320
from gpio import GPIO
from mcp3008 import MCP3008

PATH = os.path.abspath(os.path.dirname(__file__)) + '/config.ini'

__config = ConfigParser(allow_no_value=False)
__config.optionxform = str
__config.read_dict(defaults.config)

if os.path.exists(PATH):
    __config.read(PATH)
else:
    with open(PATH, 'w') as f:
        __config.write(f)

__am2320 = AM2320()
__gpio = GPIO()
__mcp3008 = MCP3008(__config)

try:
    print('Test')
finally:
    __gpio.close()
