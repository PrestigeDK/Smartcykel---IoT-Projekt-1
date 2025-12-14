from machine import ADC, Pin
from ina219_lib import INA219
from gpio_lcd import GpioLcd
from lmt87 import LMT87
import time

# Batterigrænser for LiPo
U_MIN = 3.0   # 0%
U_MAX = 4.2   # 100%


class Battery:
    def __init__(self, i2c):
        # ADC til batterispænding
        self.adc = ADC(Pin(34))
        self.adc.atten(ADC.ATTN_11DB)

        # I2C + INA219 til strøm
        self.i2c = i2c
        self.ina219 = INA219(self.i2c, 0x40)
        self.ina219.set_calibration_16V_400mA()

        # LMT87 temperatur
        self.temp = LMT87(35)

        # Kalibrering
        self.t1 = 25.2
        self.adc1 = 2659
        self.t2 = 24.2
        self.adc2 = 2697

        # Kør kalibrering én gang ved opstart
        self.temp.calibrate(self.t1, self.adc1, self.t2, self.adc2)

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
        self.cur_max = -9999.0
        self.cur_min = 9999.0
        self.cur_sum = 0.0
        self.measurements = 0

        # GPS
        self.lat = None
        self.lng = None
        self.course = None

    # Læs batterispænding
    def read_voltage(self):
        raw = self.adc.read()
        u_bat = 0.001428 * raw + 1.03
        return u_bat

    # Udregn batteriprocent
    def get_pct(self, u_bat):
        pct = (u_bat - U_MIN) / (U_MAX - U_MIN) * 100
        if pct < 0:
            pct = 0
        if pct > 100:
            pct = 100
        return pct

    # Læs temperatur (°C)
    def read_temperature(self):
        temperature = self.temp.get_temperature()
        return temperature

    # Læs strøm fra INA219 + opdater min/avg/max
    def read_current(self):
        current = self.ina219.get_current()
        if current == 0:
            current = 0.1

        self.measurements += 1

        if current < self.cur_min:
            self.cur_min = current
        elif current > self.cur_max:
            self.cur_max = current

        self.cur_sum += current
        cur_avg = self.cur_sum / self.measurements

        return current, self.cur_min, self.cur_max, cur_avg

    # Gem lat/lng/course fra main
    def set_gps(self, lat, lng, course):
        self.lat = lat
        self.lng = lng
        self.course = course

    # Opdater LCD
    def step(self):
        u_bat = self.read_voltage()
        pct = self.get_pct(u_bat)
        current, cur_min, cur_max, cur_avg = self.read_current()
        temperature = self.read_temperature()

        # Print til konsollen
        print("Battery:", round(u_bat, 2), "V |", round(pct, 1), "% |",
              "I:", round(current, 1), "mA |",
              "Temp:", temperature, "C")

        # Linje 0: Batteri + temp
        self.lcd.move_to(0, 0)
        text0 = "{:.1f}V B:{:.0f}%".format(u_bat, pct)
        self.lcd.putstr((text0 + " " * 20)[:11])   # fyld til kol 11

        self.lcd.move_to(11, 0)                    # col=11, row=0
        textT = "T:{}C".format(int(temperature))
        self.lcd.putstr((textT + " " * 9)[:9])     # resten af linjen

        # Linje 1: Strøm + avg
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
        self.lcd.putstr((text3 + " " * 12)[:12])
        
        # Linje 3: Course
        self.lcd.move_to(13, 3)
        if self.course is not None:
            text4 = "C:{:.1f}".format(self.course)
        else:
            text4 = "C: --"
        self.lcd.putstr((text4 + " " * 7)[:7])