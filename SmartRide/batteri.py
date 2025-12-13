from machine import ADC, Pin, I2C
from ina219_lib import INA219
from gpio_lcd import GpioLcd
import time

# Batterigrænser for LiPo
U_MIN = 3.0   # 0%
U_MAX = 4.2   # 100%


class Battery:
    def __init__(self, i2c):
        # ADC til batterispænding
        self.adc = ADC(Pin(34))
        self.adc.atten(ADC.ATTN_11DB)   # ~0–3.3V

        # I2C + INA219 til strøm
        self.i2c = i2c
        self.ina219 = INA219(self.i2c, 0x40)
        self.ina219.set_calibration_16V_400mA()

        # LCD på Educaboard
        self.lcd = GpioLcd(
            rs_pin=Pin(27),
            enable_pin=Pin(25),
            d4_pin=Pin(33),
            d5_pin=Pin(32),
            d6_pin=Pin(21),
            d7_pin=Pin(22),
            num_lines=4,
            num_columns=20
        )

        # Variabler til min/avg/max strøm
        self.cur_max = -9999.0      # max current
        self.cur_min = 9999.0       # min current
        self.cur_sum = 0.0          # sum af målinger
        self.measurements = 0       # antal målinger
        
        # GPS
        self.lat = None
        self.lng = None

    # Læs batterispænding
    def read_voltage(self):
        raw = self.adc.read()
        u_bat = 0.001428 * raw + 1.03   # kalibrering
        return u_bat

    # Udregn batteriprocent
    def get_pct(self, u_bat):
        pct = (u_bat - U_MIN) / (U_MAX - U_MIN) * 100
        # clamp mellem 0 og 100 %
        
        if pct < 0:
            pct = 0
        if pct > 100:
            pct = 100
        return pct

    # Læs strøm fra INA219 + opdater min/avg/max
    def read_current(self):
        current = self.ina219.get_current()

        if current == 0:
            current = 0.1

        # Opdater flow-variablerne
        self.measurements += 1
        timestamp = time.ticks_ms()

        # Tjek min, max
        if current < self.cur_min:
            self.cur_min = current
        elif current > self.cur_max:
            self.cur_max = current

        # Beregn gennemsnit
        self.cur_sum += current
        cur_avg = self.cur_sum / self.measurements

        return current, self.cur_min, self.cur_max, cur_avg
    
    # Funktion som gemmer lat & lng
    def set_gps(self, lat, lng):
        self.lat = lat
        self.lng = lng

    # Funktion som opdatere lcd med aflæste & beregnet værdier
    def step(self):
        u_bat = self.read_voltage()
        pct = self.get_pct(u_bat)
        current, cur_min, cur_max, cur_avg = self.read_current()
        
        # Linje 0: Batteri
        self.lcd.move_to(0, 0)
        text0 = "{:.1f}V B:{:.0f}%".format(u_bat, pct)
        self.lcd.putstr((text0 + " " * 20)[:20])

        # Linje 1: Strøm
        self.lcd.move_to(0, 1)
        text1 = "I:{:.0f}mA avg:{:.0f}".format(current, cur_avg)
        self.lcd.putstr((text1 + " " * 20)[:20])

        # Linje 2: Latitude
        self.lcd.move_to(0, 2)
        if self.lat is not None:
            text2 = "Lat:{:.5f}".format(self.lat)
        else:
            text2 = "Lat: ---"
        self.lcd.putstr((text2 + " " * 20)[:20])

        # Linje 3: Longitude
        self.lcd.move_to(0, 3)
        if self.lng is not None:
            text3 = "Lng:{:.5f}".format(self.lng)
        else:
            text3 = "Lng: ---"
        self.lcd.putstr((text3 + " " * 20)[:20])
