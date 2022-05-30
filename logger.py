import time
from configparser import ConfigParser
from air import Air
from led import Led
from soil import Soil
from gpiozero import Button
from signal import pause

CONFIG_PATH = 'config.ini'


class Logger:
    __BUTTON_PIN: int = 19

    def __init__(self, config: ConfigParser):
        self.config = config
        self.air = Air()
        self.soil = Soil()
        self.led = Led()
        self.button = Button(self.__BUTTON_PIN)
        self.button.when_activated = lambda: self.log()

        self.soil.moist = float(config['Logging']['Moist'])
        self.soil.dry = float(config['Logging']['Dry'])

    def connect(self):
        self.led.blink_red()
        self.led.blink_green()

        pause()

    def log(self):
        print('\n' + str(self.air.temperature) + ' C')
        print(str(self.air.humidity) + ' %')

        voltage = self.soil.voltage

        print(str(round(voltage, 2)) + ' V')
        print(str(round(self.soil.normalize(voltage), 2)) + ' %')
