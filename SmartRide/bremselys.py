from machine import Pin, I2C, PWM
from time import sleep
from mpu6050 import MPU6050
from neopixel import NeoPixel
import time

class BremselysStyring:
    def __init__(self):
        
        #I2C opsætning
        self.i2c = I2C(0, scl=Pin(18), sda=Pin(19))
        self.mpu = MPU6050(self.i2c)
        
        #LED/transistor på GPIO12
        self.red_led = PWM(Pin(12))
        self.red_led_freq = 70
        self.red_led_duty = 0

        #Tærskel for bremsing (G-force)
        self.neg_acc_threshold = -0.5
        
        # Twilight begin & end
        self.twilight_begin = None
        self.twilight_end = None
        
    # Funktion som sætter twilight variabler    
    def set_twilight(self, begin_dec, end_dec):
        self.twilight_begin = begin_dec
        self.twilight_end = end_dec
    
    # Funktion som læser MPU værdier og returnere ax
    def read_mpu(self):
        vals = self.mpu.get_values()
        ax = vals['acceleration x'] / 16384
        return ax
    
    # Funktion der tjekker om vi bremser
    def braking(self, ax):
        return ax < self.neg_acc_threshold
    
    # Funktion som tjekker om det er dag/nat
    def day_or_night(self):
        if self.twilight_begin is None or self.twilight_end is None:
            return None
        
        nu = time.localtime()
        nu_min = nu[3] * 60 + nu[4]

        begin_min = self.twilight_begin * 60
        end_min = self.twilight_end * 60

        return begin_min <= nu_min < end_min

    # Funktion som vælger farve ift. om vi bremser og om det er dag/nat
    def choose_duty(self, day, braking):
        r, g, b = (0, 0, 0)
        # Hvis ingen data på dag, så sætter vi stadig lyset til svagt
        if day is None:
            self.red_led_duty = 256
        # Hvis det er dag og vi ikke bremser, så er lyset slukket
        elif day == True and not braking:
            self.red_led_duty = 0
        # Hvis det er dag og vi bremser, så sætter vi lyset til kraftigt
        elif day == True and braking == True:
            self.red_led_duty = 1023
        # Hvis det ikke er dag og vi ikke bremser, sætter vi lyset til svagt
        elif day == False and not braking:
            self.red_led_duty = 256
        # Hvis det ikke er dag og vi bresmer, sætter vi lyset til kraftigt
        elif day == False and braking == True:
            self.red_led_duty = 1023
    
        return (self.red_led_duty)
    
    # Funktion som styrer logik og bruger tidligere funktioner i klassen
    def step(self):
        ax = self.read_mpu()
        braking = self.braking(ax)
        day = self.day_or_night()
        self.red_led_duty = self.choose_duty(day, braking)

        
