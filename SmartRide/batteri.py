from machine import ADC, Pin, I2C
from ina219_lib import INA219
from lmt87 import LMT87
import time

class Battery:
    def __init__(self):
        
        # Batterigrænser for LiPo
        self.u_min = 3.0   # 0%
        self.u_max = 4.2   # 100%
        
        self.pin_bat = 34
        self.adc = ADC(Pin(self.pin_bat))
        
        self.i2c_port = 0 # The I2C port number
        self.ina219_i2c_addr = 0x40 # The INA219 I2C address
        
        # Calibration values
        self.t1 = 25.2
        self.adc1 = 2659
        self.t2 = 24.2
        self.adc2 = 2697
        
        self.pin_lmt87 = 35
        self.temp = LMT87(pin_lmt87)
        
        # Variabler
        self.cur_max = -9999 # The max current
        self.cur_min = 9999  # The min current
        self.cur_sum = 0 # The sum of current measurements
        self.measurements = 0 # Number of measurements

    # Funktion som læser adc værdier
    def adc_read(self):
        raw = self.adc.read()
        u_bat = 0.001428 * raw + 1.03
        
        return u_bat
        
    # Funktion som udregner batteriprocent   
    def battery_procent(self):
        pct = (u_bat - self.u_min) / (self.u_max - self.u_min) * 100
        pct = max(0, min(100, pct)) # clamp mellem 0 og 100%
        
        return pct
    
    # Funktion som læser INA værdier
    def get_values(self):
        current = self.ina219.get_current()
        shunt_voltage = self.ina219.get_shunt_voltage()
        bus_voltage = self.ina219.get_bus_voltage()
        
        if current == 0:
            current = 0.1
        
        # Update the flow variables
        self.measurements += 1 # Increment the counter
        timestamp = time.ticks_ms() # Get the relative time stamp
        
        # Check min, max and calc average
        if current < self.cur_min:
            self.cur_min = current
        elif current > self-cur_max:
            self.cur_max = current
        
        self.cur_sum += current
        cur_avg = self.cur_sum / self.measurements
