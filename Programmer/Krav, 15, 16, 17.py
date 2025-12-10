from machine import Pin, I2C, RTC, PWM
from time import sleep
from mpu6050 import MPU6050
import utime
import requests
from neopixel import NeoPixel

#I2C opsætning
i2c = I2C(0, scl=Pin(18), sda=Pin(19))
mpu = MPU6050(i2c)


#LED/transistor på GPIO26
antal_pixels = 2
np = NeoPixel(Pin(26, Pin.OUT), antal_pixels)
def set_color(r, g, b, antal_pixels):
    for i in range(antal_pixels):       # Loop gennem det ønskede antal LED'er
        np[i] = (r, g, b)               # Sæt farven til (rød, grøn, blå)
    np.write() 

#Vælg tærskel for bremsing
Neg_acc_threshold = -0.5   #G-force

def solop_solned_data():
    url = 'https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400'
    v = requests.get(url)
    data = v.json()
    res = data['results']
    return res["civil_twilight_begin"], res["civil_twilight_end"]

def tid_til_decimaltal(tid_str: str) -> float:
    tid_split, ampm = tid_str.split()
    t, m, s = map(int, tid_split.split(':'))
    
    if ampm == 'PM' and t != 12:
        t += 12
    if ampm == 'AM' and t == 12:
        t = 0
    
    return t + m / 60
    
solop, solned = solop_solned_data()
solop_min = tid_til_decimaltal(solop)
solned_min = tid_til_decimaltal(solned)

sidste_tid = utime.time()

while True:
    if utime.time() - sidste_tid > 600:
        solop, solned = solop_solned_data()
        solop_min = tid_til_decimaltal(solop)
        solned_min = tid_til_decimaltal(solned)
        sidste_tid = utime.time()
        
    nu = utime.localtime()
    nu_min =nu[3]*60 + nu[4]
    
    vals = mpu.get_values()
    
    ax = vals['acceleration x'] / 16384
    ay = vals['acceleration y'] / 16384
    az = vals['acceleration z'] / 16384

    bremse = ax < Neg_acc_threshold
    print('ax', ax, 'ay', ay, 'az', az, bremse)
    
    if solop_min <= nu_min < solned_min:
        if bremse:
            set_color(255, 0, 0, antal_pixels)
            #bremse_lys_duty = 1023
            
        else:
            set_color(0, 0, 0, antal_pixels)
            #bremse_lys_duty = 0
    else:
        if bremse:
            set_color(255, 0, 0, antal_pixels)
            #bremse_lys_duty = 1023
        else:
            set_color(64, 0, 0, antal_pixels)
            #bremse_lys_duty = 256
    
    sleep(0.3)
    