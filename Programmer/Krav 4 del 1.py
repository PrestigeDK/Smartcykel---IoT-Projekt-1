from machine import Pin, I2C
from time import sleep, time
from mpu6050 import MPU6050


POWER_KNAP = 4
power_knap = Pin(POWER_KNAP, Pin.IN, Pin.PULL_UP)

STILLE_TID = 180
system_on = False
stille_tid = time.time()

i2C = I2C (0, scl=Pin(18), sda=Pin(19))
mpu = MPU6050(i2c)

Neg_acc_threshold = - 0.5

#print(system_on)

while True:
    if not power_knap.value():
        system_on = not system_on
        print("System er tændt" if system_on else "System er slukket")
        sleep(0.5)
        
        
    if not system_on:
        sleep(0.2) 
        continue
    
    vals = mpu.get_values()
    
    ax = vals['acceleration x'] / 16384
    
    if not moving:
        stille_tid = time.time()
        
    if time.time() - stille_tid > STILLE_TID:
        if moving:
            print('Cykel rykkes')
            
            
    
    