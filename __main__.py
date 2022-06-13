#!/usr/bin/env python3
import configparser
import os
import sys
from configparser import ConfigParser
from signal import pause

from config import PATH, CONFIG
from logger import Logger

__config = ConfigParser(allow_no_value=True)
__config.optionxform = str
__config.read_dict(CONFIG)

if os.path.exists(PATH):
    print('Reading config.ini')

    try:
        __config.read(PATH)

        if len(__config.get('Logging', 'LoggerId')) == 0:
            sys.exit('Logger ID has not been set')
    except configparser.Error as e:
        sys.exit(str(e))
else:
    print('Writing new config file')

    with open(PATH, 'w') as f:
        __config.write(f)

try:
    with Logger(__config) as logger:
        pause()
except KeyboardInterrupt:
    sys.exit()
