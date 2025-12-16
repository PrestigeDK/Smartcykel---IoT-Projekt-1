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

def set_np_color(r, g, b):
    for i in range(antal_pixels):
        np[i] = (r, g, b)
    np.write()

def write_line(row: int, text: str):
    if not isinstance(text, str):
        text = str(text)
    s = text[:20]
    pad_len = 20 - len(s)
    if pad_len > 0:
        s = s + (" " * pad_len)
    lcd.move_to(0, row)
    lcd.putstr(s)

def show_data_on_lcd(co2, status, relay_on):
    write_line(0, "CO2: {:>5.1f} g/kWh".format(co2))
    write_line(1, " ")
    write_line(2, "Status: {}".format(status))
    write_line(3, "Relay: {}".format("ON" if relay_on else "OFF"))

while True:
    try:
        resp_co2 = requests.get('https://api.energidataservice.dk/dataset/CO2Emis?limit=2')
        data_co2 = resp_co2.json()
        co2_value = float(data_co2['records'][1]['CO2Emission'])
    except Exception as e:
        co2_value = 999.00
        print("CO2 fetch error:", e)

    is_green = co2_value <= CO2_MAX_G_PER_KWH

    if is_green:
        set_np_color(0, 255, 0)
        relay.on()
        status = "Green Energy"
    else:
        set_np_color(255, 0, 0)
        relay.off()
        status = "Not Green"

    show_data_on_lcd(co2_value, status, relay.value() == 1)

    print("CO2:{:.1f} g/kWh | Green:{} | Relay:{}"
          .format(co2_value, is_green, relay.value()))

    sleep(5)
    