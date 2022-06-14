#!/usr/bin/env python3
import configparser
import os
import sys
from configparser import ConfigParser
from signal import pause

from config import PATH, CONFIG
from logger import Logger

__config = ConfigParser(allow_no_value=True)
__config.optionxform = str  # When writing to a file, make sure that options are written case sensitively
__config.read_dict(CONFIG)  # Read default values in case there's no config file in the filesystem

if os.path.exists(PATH):
    print('Reading config.ini')

    try:
        __config.read(PATH)  # Reads a config file at the given path

        if len(__config.get('Logging', 'LoggerId')) == 0:
            sys.exit('Logger ID has not been set')  # Script should not run if the logger hasn't been assigned an ID
    except configparser.Error as e:
        sys.exit(str(e))
else:
    print('Writing new config file')

    with open(PATH, 'w') as f:
        __config.write(f)  # Write the defaults to the given path if no file exists

try:
    with Logger(__config) as logger:  # Initialize a Logger instance with a with statement for guaranteed cleanup
        pause()  # Pauses the main thread so the script doesn't stop
except KeyboardInterrupt:
    sys.exit()
