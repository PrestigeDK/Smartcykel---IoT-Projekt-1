from machine import ADC, Pin
from machine import I2C
from ina219_lib import INA219
import time
from time import sleep
from machine import UART
from gps_simple import GPS_SIMPLE
from time import sleep
from lmt87 import LMT87
from machine import Pin
from gpio_lcd import GpioLcd

PIN_BAT = 34
VREF = 3.3,
ADC_MAX = 4095

adc = ADC(Pin(PIN_BAT))
adc.atten(ADC.ATTN_11DB)   # giver ca. 0–3.3V måleområde

# Spændingsdeler-faktor (R1=10k, R2=10k)
FAKTOR = 2   


# Batterigrænser for LiPo
U_MIN = 3.0   # 0%
U_MAX = 4.2   # 100%

# CONFIGURATION
i2c_port = 0                           # The I2C port number, and thus pins

ina219_i2c_addr = 0x40                 # The INA219 I2C address

delimiter = '\t'                       # The dump delimiter

#########################################################################
# OBJECTS
i2c = I2C(i2c_port)                    # I2C bus

ina219 = INA219(i2c, ina219_i2c_addr)  # The INA219 object

#########################################################################
# VARIABLES
cur_max = -9999                        # The max current
cur_min = 9999                         # The min current
cur_sum = 0                            # The sum of current measurements

measurements = 0                       # Number of measurements 

###########################################################
# PROGRAM
print("\nINA219 dynamic current monitoring program\n")

ina219.set_calibration_16V_400mA()     # Set a more sensitive range

#########################################################################
# CONFIGURATION
gps_port = 2                                 # ESP32 UART port, Educaboard ESP32 default UART port
gps_speed = 9600                             # UART speed, defauls u-blox speed
#########################################################################
# OBJECTS
uart = UART(gps_port, gps_speed)             # UART object creation
gps = GPS_SIMPLE(uart)                      # GPS object creation
#########################################################################    
# PROGRAM
# CONFIGURATION
pin_lmt87 = 35

# Calibration values
t1 = 25.2
adc1 = 2659
t2 = 24.2
adc2 = 2697

# OBJECTS
temp = LMT87(pin_lmt87)


# Create the LCD object
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32), d6_pin=Pin(21), d7_pin=Pin(22),
              num_lines=4, num_columns=20)

# PROGRAM
while True:
    raw = adc.read()                    
    
    u_bat = 0.001428 * raw + 1.03

    # Udregn batteriprocent
    pct = (u_bat - U_MIN) / (U_MAX - U_MIN) * 100
    pct = max(0, min(100, pct)) # clamp mellem 0 og 100%


    lcd.move_to(0,0)
    # ,"\tU_bat:", round(u_bat, 3), "V","\tBatteri:", round(pct, 1), "%
    lcd.putstr(f"{round(u_bat,1)}V B:{round(pct, 1)}% ")

    sleep(2)
    lcd.clear()
    sleep (3)

    # Get the values
    current = ina219.get_current()
    shunt_voltage = ina219.get_shunt_voltage()
    bus_voltage = ina219.get_bus_voltage()
    
    # Update the flow variables
    measurements += 1                  # Increment the counter
    timestamp = time.ticks_ms()        # Get the relative time stamp
    
    # Check min, max and calc average
    if current < cur_min:
        cur_min = current
    elif current > cur_max:
        cur_max = current
        
    cur_sum += current
    cur_avg = cur_sum / measurements
    
    
    if gps.receive_nmea_data():
        print(f"UTC YYYY-MM-DD  : {gps.get_utc_year()}-{gps.get_utc_month():02d}-{gps.get_utc_day():02d}")
        print(f"UTC HH:MM:SS    : {gps.get_utc_hours()}:{gps.get_utc_minutes():02d}:{gps.get_utc_seconds():02d}")
        lcd.move_to(0,1)
        lcd.putstr(f"La:{gps.get_latitude():.4f}")
        lcd.move_to(0,8)
        lcd.putstr(f"L:{gps.get_longitude():.4f}")
        print(f"Validity        : {gps.get_validity()}")
        lcd.move_to(0,3)
        lcd.putstr(f"Speed:km/t{gps.get_speed()}")
        lcd.move_to(10,0)
        lcd.putstr(f"C: {gps.get_course():.1f}\n")
        lcd.move_to(0,4)
        print(f"INA: {ina219.get_current()}")
        print("LMT87 test\n")
        print(temp.calibrate(t1, adc1, t2, adc2))
        adc_val = temp.get_adc_value()
        temperature = temp.get_temperature ()
        lcd.move_to(0,2)
        lcd.putstr("Temp: %d °C" %(temperature))
        
        sleep(3)


    # Print the data (ought to be to a file instead)
    #print("INA %d%s%d%s%f%s%f" % (measurements, delimiter, timestamp, delimiter, bus_voltage, delimiter, current))
    
    #print("INA \t\t\t\t\t\t%.2f %.2f %.2f" % (cur_min, cur_max, cur_avg))
    
print(f"INA: {ina219.get_current()}")
sleep(0.2)                         # Should not be present. Measure as fast as possible

# if gps.receive_nmea_data():
#         print(f"UTC YYYY-MM-DD  : {gps.get_utc_year()}-{gps.get_utc_month():02d}-{gps.get_utc_day():02d}")
#         print(f"UTC HH:MM:SS    : {gps.get_utc_hours()}:{gps.get_utc_minutes():02d}:{gps.get_utc_seconds():02d}")
#         print(f"Latitude        : {gps.get_latitude():.8f}")
#         print(f"Longitude       : {gps.get_longitude():.8f}")
#         print(f"Validity        : {gps.get_validity()}")
#         print(f"Speed           : km/t {gps.get_speed()}")
#         print(f"Course          : {gps.get_course():.1f}\n")
#         print(f"INA: {ina219.get_current()}")