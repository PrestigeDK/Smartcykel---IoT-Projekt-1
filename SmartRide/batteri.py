from machine import ADC, Pin
from ina219_lib import INA219
from gpio_lcd import GpioLcd
from lmt87 import LMT87
import time

U_MIN = 3.0
U_MAX = 4.2

class Battery:
    def __init__(self, i2c):
        self.adc = ADC(Pin(34))
        self.adc.atten(ADC.ATTN_11DB)

        self.i2c = i2c
        self.ina219 = INA219(self.i2c, 0x40)
        self.ina219.set_calibration_16V_400mA()

        self.temp = LMT87(35)

        self.t1 = 25.2
        self.adc1 = 2659
        self.t2 = 24.2
        self.adc2 = 2697
        self.temp.calibrate(self.t1, self.adc1, self.t2, self.adc2)

        self.lcd = GpioLcd(
            rs_pin=Pin(27),
            enable_pin=Pin(25),
            d4_pin=Pin(33),
            d5_pin=Pin(32),
            d6_pin=Pin(21),
            d7_pin=Pin(22),
            num_lines=4,
            num_columns=20)

        self.cur_max = -9999.0
        self.cur_min = 9999.0
        self.cur_sum = 0.0
        self.measurements = 0

        self.lat = None
        self.lng = None
        self.course = None
        self.speed = None

        self.lcd_page = 0
        self.lcd_last_switch = time.time()
        self.lcd_switch_s = 5.0

    def read_voltage(self):
        raw = self.adc.read()
        u_bat = 0.00161 * raw + 0.27961
        return u_bat

    def get_pct(self, u_bat):
        pct = (u_bat - U_MIN) / (U_MAX - U_MIN) * 100
        if pct < 0:
            pct = 0
        if pct > 100:
            pct = 100
        return pct

    def read_temperature(self):
        return self.temp.get_temperature()

    def read_current(self):
        current = self.ina219.get_current()

        if current == 0:
            current = 0.1

        self.measurements += 1

        if current < self.cur_min:
            self.cur_min = current
        if current > self.cur_max:
            self.cur_max = current

        self.cur_sum += current
        cur_avg = self.cur_sum / self.measurements

        return current, self.cur_min, self.cur_max, cur_avg

    def set_gps(self, lat, lng, course, speed):
        self.lat = lat
        self.lng = lng
        self.course = course
        self.speed = speed

    def rest_tid(self, pct, current_ma):
        if current_ma is None or current_ma <= 0:
            return None
        remaining_mah = (pct / 100.0) * 2000.0
        return remaining_mah / current_ma 

    def _lcd_line(self, row, text):
        text = (text + " " * 20)[:20]
        self.lcd.move_to(0, row)
        self.lcd.putstr(text)

    def display_status(self, pct, u_bat, current_ma, temperature_c):
        now = time.time()

        if now - self.lcd_last_switch >= self.lcd_switch_s:
            self.lcd_page = (self.lcd_page + 1) % 2
            self.lcd_last_switch = now
            self.lcd.clear()

        if self.lcd_page == 0:
            self._lcd_line(0, f"BAT:{pct:5.1f}%  T:{temperature_c:4.1f}")
            self._lcd_line(1, f"U:{u_bat:4.2f}V  I:{current_ma:4.0f}mA")

            rt = self.rest_tid(pct, current_ma)
            if rt is None:
                rt_txt = "RT: --"
            else:
                h = int(rt)
                m = int((rt - h) * 60)
                rt_txt = f"RT:{h}h{m:02d}m"
            self._lcd_line(2, rt_txt)
            self._lcd_line(3, "Side 1/2")

        else:
            if self.speed is None:
                self._lcd_line(0, "Speed: --")
            else:
                self._lcd_line(0, f"Speed:{self.speed:6.2f}")

            if self.lat is None:
                self._lcd_line(1, "Lat: --")
            else:
                self._lcd_line(1, f"Lat:{self.lat: .5f}")

            if self.lng is None:
                self._lcd_line(2, "Lng: --")
            else:
                self._lcd_line(2, f"Lng:{self.lng: .5f}")

            if self.course is None:
                self._lcd_line(3, "Crs: --  Side 2/2")
            else:
                self._lcd_line(3, f"Crs:{self.course:5.1f} Side 2/2")

    def step(self):
        u_bat = self.read_voltage()
        pct = self.get_pct(u_bat)
        current_ma, cur_min, cur_max, cur_avg = self.read_current()
        temperature_c = self.read_temperature()
        self.display_status(pct, u_bat, current_ma, temperature_c)