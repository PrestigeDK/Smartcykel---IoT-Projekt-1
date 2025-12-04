from machine import Pin, I2C
from time import sleep
from mpu6050 import MPU6050
from solop_solned import Solop_Solned

#I2C opsætning
i2c = I2C(0, scl=Pin(18), sda=Pin(19))
mpu = MPU6050(i2c)

sol = Solop_Solned()
url = "https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400"
sol_data = sol.data_fra_api(url)


#LED/transistor på GPIO12
bremse_lys = Pin(12, Pin.OUT)

#Vælg tærskel for bremsing
Neg_acc_threshold = -0.5   #G-force

while True:
    vals = mpu.get_values()
    
    ax = vals['acceleration x'] / 16384
    ay = vals['acceleration y'] / 16384
    az = vals['acceleration z'] / 16384
    
    #Vi bruger ax som er X-aksen til frem/bagud acceleration
    #Dog skal der tages højde for hvordan MPU6050 sidder på cyklen
    if ax < Neg_acc_threshold:
        bremse_lys.on()
        sleep(1)
    else:
        bremse_lys.off()
        sleep(1)
    print('ax', ax, 'ay', ay, 'az', az)
    sleep(0.1)

