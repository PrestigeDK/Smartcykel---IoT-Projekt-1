import requests, json
from time import sleep
from neopixel import NeoPixel
from gpio_lcd import GpioLcd
from lcd_api import LcdApi
from machine import Pin

CO2_MAX_G_PER_KWH = 50.0

np = NeoPixel(Pin(26, Pin.OUT), 1)
antal_pixels = 1

relay = Pin(14, Pin.OUT)

lcd = GpioLcd(rs_pin=Pin(27),
              enable_pin=Pin(25),
              d4_pin=Pin(33),
              d5_pin=Pin(32),
              d6_pin=Pin(21),
              d7_pin=Pin(22),
              num_lines=4,
              num_columns=20)

test_data = [{'CO2Emission': 40.0},
             {'CO2Emission': 60.0},
             {'CO2Emission': 35.0},
             {'CO2Emission': 80.0}]
cycle = 0

def set_np_color(r, g, b):
    for i in range(antal_pixels):
        np[i] = (r, g, b)
    np.write()

def lcd_write(line, col, text, bredde=20):
    lcd.move_to(col, line)
    lcd.putstr((str(text) + " " * bredde)[:bredde])

while True:
    case = test_data[cycle % len(test_data)]
    cycle += 1

    co2_value = float(case['CO2Emission'])
    is_green = co2_value <= CO2_MAX_G_PER_KWH

    if is_green:
        set_np_color(0, 255, 0)
        relay.on()
        status = "Green"
        relay_txt = "On"
    else:
        set_np_color(255, 0, 0)
        relay.off()
        status = "Red"
        relay_txt = "Off"

    lcd_write(0, 0, "CO2: {:.1f} g/kWh".format(co2_value))
    lcd_write(1, 0, "Status: {}".format(status))
    lcd_write(2, 0, "Relay: {}".format(relay_txt))
    lcd_write(3, 0, "Cycle: {}".format(cycle))

    sleep(2)