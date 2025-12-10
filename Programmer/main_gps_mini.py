# GPS program
from machine import UART
from gps_simple import GPS_SIMPLE
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
while True:
    if gps.receive_nmea_data():
        print(f"UTC YYYY-MM-DD  : {gps.get_utc_year()}-{gps.get_utc_month():02d}-{gps.get_utc_day():02d}")
        print(f"UTC HH:MM:SS    : {gps.get_utc_hours()}:{gps.get_utc_minutes():02d}:{gps.get_utc_seconds():02d}")
        print(f"Latitude        : {gps.get_latitude():.8f}")
        print(f"Longitude       : {gps.get_longitude():.8f}")
        print(f"Validity        : {gps.get_validity()}")
        print(f"Speed           : km/t {gps.get_speed()}")
        print(f"Course          : {gps.get_course():.1f}\n")