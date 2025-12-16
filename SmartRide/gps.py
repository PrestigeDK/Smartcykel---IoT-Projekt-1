from machine import UART
from gps_simple import GPS_SIMPLE
import time
import math

class GpsReader:
    def __init__(self, uart_port=2, baudrate=9600):
        self.uart = UART(uart_port, baudrate)
        self.gps = GPS_SIMPLE(self.uart)
        
    def get_data(self, timeout_s=20):
        start = time.time()
        while time.time() - start < timeout_s:
            if self.gps.receive_nmea_data():
                validity = self.gps.get_validity()
                if validity in ("A", 1, True):
                    lat = self.gps.get_latitude()
                    lng = self.gps.get_longitude()
                    course = self.gps.get_course()
                    speed = self.gps.get_speed()
                    return lat, lng, speed, course
        return None, None, None, None
    
    def read_valid(self, timeout_s=3):
        lat, lng, speed, course = self.get_data(timeout_s)
        valid = (lat is not None) and (lng is not None)
        return valid, lat, lng, speed, course

    def haversine(self, lat1, lng1, lat2, lng2):
        R = 6371000
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        a = (math.sin(dlat / 2) ** 2) + (math.cos(lat1) * math.cos(lat2) * (math.sin(dlng / 2) ** 2))
        c = 2 * math.asin(math.sqrt(a))
        return R * c