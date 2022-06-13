import os
from configparser import ConfigParser

PATH = os.path.abspath(os.path.dirname(__file__)) + '/config.ini'

CONFIG = {
    'Logging': {
        'LoggerId': '',
        'PairingId': '',
        'Active': False,
        'SocketUrl': '20.4.59.10:9093',
        'RestUrl': '20.4.59.10:9092'
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
    }
}


def to_dict(config: ConfigParser) -> dict:
    return {
        'Logging': {
            'LoggerId': config.get('Logging', 'LoggerId'),
            'PairingId': config.get('Logging', 'PairingId'),
            'Active': config.getboolean('Logging', 'Active'),
            'SocketUrl': config.get('Logging', 'SocketUrl'),
            'RestUrl': config.get('Logging', 'RestUrl')
        },
        'Air': {
            'MinHumid': config.getfloat('Air', 'MinHumid'),
            'MaxHumid': config.getfloat('Air', 'MaxHumid'),
            'MinTemp': config.getfloat('Air', 'MinTemp'),
            'MaxTemp': config.getfloat('Air', 'MaxTemp')
        },
        'Soil': {
            'Moist': config.getfloat('Soil', 'Moist'),
            'Dry': config.getfloat('Soil', 'Dry')
        }
    }
