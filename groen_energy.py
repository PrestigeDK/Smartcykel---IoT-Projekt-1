import requests, json
from time import sleep
from neopixel import NeoPixel
from gpio_lcd import GpioLcd
from lcd_api import LcdApi
from machine import Pin

# Config thresholds
CO2_MAX_G_PER_KWH = 50.0           # Grøn energi grænse
PRICE_MAX_DKK_PER_MWH = 600.0       # Lav pris grænse (DKK/MWh)

# Laver NeoPixel objekt.
np = NeoPixel(Pin(26, Pin.OUT), 1)
antal_pixels = 1

#Laver relæ objekt.
relay = Pin(14, Pin.OUT)

# Laver LCD objekt.
lcd = GpioLcd(rs_pin=Pin(27),
              enable_pin=Pin(25),
              d4_pin=Pin(33),
              d5_pin=Pin(32),
              d6_pin=Pin(21),
              d7_pin=Pin(22),
              num_lines=4,
              num_columns=20)

# Funktion der sætter NeoPixel'ens farve.
def set_np_color(r, g, b):
    for i in range(antal_pixels):
        np[i] = (r, g, b)
    np.write()

# Funktion der skriver én hel linje, samt undgår 'snavs' fra tidligere.
def write_line(row: int, text: str):
    # Sørger for at det er en string.
    if not isinstance(text, str):
        text = str(text)
    # Trimmer og tilføjer så det er præcist 20 karakterer.
    s = text[:20]
    pad_len = 20 - len(s)
    if pad_len > 0:
        s = s + (" " * pad_len)
    lcd.move_to(0, row)
    lcd.putstr(s)
    
#Funktion der viser tekst/data på skærm.
def show_data_on_lcd(co2, price_dkk, status, relay_on):
    write_line(0, "CO2: {:>5.1f} g/kWh".format(co2))
    write_line(1, "Price: {:>6.2f} DKK/MWh".format(price_dkk))
    write_line(2, "Status: {}".format(status))
    write_line(3, "Relay: {}".format("ON" if relay_on else "OFF"))
        
while True:
    try:
        # CO2
        resp_co2 = requests.get(url = 'https://api.energidataservice.dk/dataset/CO2Emis?limit=2')
        data_co2 = resp_co2.json()
        co2_value = float(data_co2['records'][1]['CO2Emission'])
    except Exception as e:
        co2_value = 999.00
        print("CO2 fetch error:", e)
    
    try:
        #Elpris
        resp_el = requests.get('https://api.energidataservice.dk/dataset/Elspotprices?limit=2')
        data_el = resp_el.json()
        price_mwh = float(data_el['records'][1]['SpotPriceDKK'])
    except Exception as e:
        price_mwh = 9999.0
        print("Price fetch error:", e)
    
    is_green = co2_value <= CO2_MAX_G_PER_KWH
    is_cheap = price_mwh <= PRICE_MAX_DKK_PER_MWH
    charging = is_green and is_cheap

    if is_green:
        set_np_color(0, 255, 0)
    else:
        set_np_color(255, 0, 0)

    if charging:
        status = "Green & Cheap"
        relay.on()
    else:
        if not is_green and not is_cheap:
            status = "Not Green & Expensive"
        elif not is_green:
            status = "Not Green"
        else:
            status = "Expensive"
        relay.off()
    
    
    # LCD opdatering
    show_data_on_lcd(co2_value, price_mwh, status, relay.value() == 1)

    # Printer til shell
    print(
        "CO2:{:.1f} g/kWh | Pris:{:.1f} DKK/MWh | Green:{} | Cheap:{} | Relay:{}"
        .format(co2_value, price_mwh, is_green, is_cheap, relay.value())
    )

    # 5 sekunders interval
    sleep(5)
