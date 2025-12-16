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
        
        self.speed = None
        
        # LCD-sider
        self.lcd_page = 0
        self.lcd_last_switch = time.time()
        self.lcd_switch_s = 5.0

    # Læs batterispænding
    def read_voltage(self):
        raw = self.adc.read()
        u_bat = 0.27961 * raw + 0.00161
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

    # Gem lat/lng/course/speed fra main
    def set_gps(self, lat, lng, course, speed):
        self.lat = lat
        self.lng = lng
        self.course = course
        self.speed = speed
    
    def rest_tid(self, pct, current):
        if current <= 0:
            return None
        remaining_mah = (pct / 100) * 2000
        return remaining_mah / current
    
    def display_status(self, pct, u_bat, current, temperature, speed):
        now = time.time()
        if now - self.lcd_last_switch >= self.lcd_switch_s:
            self.lcd_page = (self.lcd_page + 1) % 2
            self.lcd_last_switch = now
            self.lcd.clear()

        # Side 1: BAT + U + I + RT
        if self.lcd_page == 1:
            self.lcd.move_to(0, 0)
            self.lcd.putstr(f"BAT:{pct:5.1f}%  T:{temperature:4.1f}")

            self.lcd.move_to(0, 1)
            self.lcd.putstr(f"U:{u_bat:4.2f}V  I:{current:4.0f}mA")

            rt = self.rest_tid(pct, current)
            self.lcd.move_to(0, 2)
            if rt is None:
                self.lcd.putstr("RT: --")
            else:
                h = int(rt)
                m = int((rt - h) * 60)
                self.lcd.putstr(f"RT:{h}h{m:02d}m")

            self.lcd.move_to(12, 3)
            self.lcd.putstr("Side 1/2")

        # Side 2: GPS info
        else:
            self.lcd.move_to(0, 0)
        if self.speed is None:
            self.lcd.putstr("Speed: --")
        else:
            self.lcd.putstr(f"Speed:{self.speed:6.2f}")

        self.lcd.move_to(0, 1)
        if self.lat is None:
            self.lcd.putstr("Lat: --")
        else:
            self.lcd.putstr(f"Lat:{self.lat: .5f}")

        self.lcd.move_to(0, 2)
        if self.lng is None:
            self.lcd.putstr("Lng: --")
        else:
            self.lcd.putstr(f"Lng:{self.lng: .5f}")

        self.lcd.move_to(0, 3)
        if self.course is None:
            self.lcd.putstr("Crs: --     Side 2/2")
        else:
            self.lcd.putstr(f"Crs:{self.course:5.1f} 2/2")

    def step(self):
        u_bat = self.read_voltage()
        pct = self.get_pct(u_bat)
        current, cur_min, cur_max, cur_avg = self.read_current()
        temperature = self.read_temperature()
        speed = self.speed
        
        self.display_status(pct, u_bat, current, temperature, speed)

        speed_print = round(speed, 2) if speed is not None else None

        print("Battery:", round(u_bat, 2), "V |", round(pct, 1), "% |", "I:", round(current, 1), "mA |", "Temp:", temperature, "C |","Speed:", speed_print)
