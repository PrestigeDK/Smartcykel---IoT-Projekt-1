from machine import Pin, I2C, PWM
from mpu6050 import MPU6050
import time

class BremselysStyring:
    def __init__(self, i2c):
        
        self.i2c = i2c
        self.mpu = MPU6050(self.i2c)
        
        self.red_led = PWM(Pin(12))
        self.red_led_freq = 70
        self.red_led_duty = 0
        self.red_led.duty(self.red_led_duty)

        self.neg_acc_threshold = -0.5
        self.brake_time_s = 1
        self.last_brake_time = None
        
        self.twilight_begin = None
        self.twilight_end = None
          
    def set_twilight(self, begin_dec, end_dec):
        self.twilight_begin = begin_dec
        self.twilight_end = end_dec
    
    def read_mpu(self):
        vals = self.mpu.get_values()
        ax = vals['acceleration x'] / 16384
        return ax
    
    def braking(self, ax):
        return ax < self.neg_acc_threshold
    
    def brake_active(self, braking):
        now = time.ticks_ms()

        if braking:
            self.last_brake_time = now
            return True

        if self.last_brake_time is None:
            return False

        return time.ticks_diff(now, self.last_brake_time) < int(self.brake_time_s * 1000)

    def day_or_night(self):
        if self.twilight_begin is None or self.twilight_end is None:
            return None
        
        nu = time.localtime()
        nu_min = nu[3] * 60 + nu[4]

        begin_min = self.twilight_begin * 60
        end_min = self.twilight_end * 60

        return begin_min <= nu_min < end_min

    def choose_duty(self, day, braking):
        if day is None:
            self.red_led_duty = 126
        elif day == True and not braking:
            self.red_led_duty = 0
        elif day == True and braking == True:
            self.red_led_duty = 1023
        elif day == False and not braking:
            self.red_led_duty = 126
        elif day == False and braking == True:
            self.red_led_duty = 1023
        return (self.red_led_duty)
    
    def step(self):
        ax = self.read_mpu()
        braking_now = self.braking(ax)
        braking = self.brake_active(braking_now)

        day = self.day_or_night()

        self.red_led_duty = self.choose_duty(day, braking)
        self.red_led.duty(self.red_led_duty)


        