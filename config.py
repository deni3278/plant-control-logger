import atexit
import logging
import os
from configparser import ConfigParser


class Config(ConfigParser):
    _DEFAULTS = {
        'Logging': {
            'LoggerId': str(),
            'PairingId': str(),
            'Active': bool(),
            'SocketUrl': str(),
            'RestUrl': str()
        },
        'Air': {
            'MinHumid': float(),
            'MaxHumid': float(),
            'MinTemp': float(),
            'MaxTemp': float()
        },
        'Soil': {
            'Moist': float(),
            'Dry': float()
        }
    }

    def __init__(self, path: str = None):
        super().__init__(allow_no_value=True)
        self.optionxform = str  # Ensures that options are written to a file case sensitively.
        self._path = path or os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))

        self.read_dict(self._DEFAULTS)
        files = self.read(self._path)

        if len(files) == 0:
            self.save()     # If no file was read, it means that there isn't one and is therefore created.
        else:
            self.clean()

        atexit.register(self.save)  # Register the save method as a handler for when the script is exiting.

    def save(self):
        self.clean()

        with open(self._path, 'w') as f:
            self.write(f)

        logging.info('Saved configuration options to \'{0}\'.'.format(self._path))

    def clean(self):
        for section in self.sections():
            if section not in self._DEFAULTS:
                self.remove_section(section)
            else:
                for option in self.options(section):
                    if option not in self._DEFAULTS[section]:
                        self.remove_option(section, option)

    def to_dict(self) -> dict:
        # noinspection PyShadowingNames
        def get_value(value, section: str, option: str):
            if type(value) == str:
                return self.get(section, option) or str()
            elif type(value) == bool:
                return self.getboolean(section, option) or bool()
            elif type(value) == float:
                return self.getfloat(section, option) or float()
            elif type(value) == int:
                return self.getint(section, option) or int()

        output = dict(self._DEFAULTS)

        for section in output:
            for option in output[section]:
                output[section][option] = get_value(output[section][option], section, option)

        return output
