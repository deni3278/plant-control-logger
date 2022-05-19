from air import Air
from led import Led
from soil import Soil

red_pin = 21
green_pin = 26
air = Air()
soil = Soil()
led = Led(red_pin, green_pin)


def log():
    print('\n' + str(air.measure_temp()) + ' C')
    print(str(air.measure_humidity()) + ' %')
    print(str(round(soil.measure_voltage(), 2)) + ' V')
    print(str(round(soil.normalize(soil.measure_voltage()), 2)) + ' %')


try:
    log()

finally:
    led.cleanup()
