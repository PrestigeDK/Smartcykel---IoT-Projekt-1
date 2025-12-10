from machine import UART
from gps_simple import GPS_SIMPLE
import time

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
                    speed = self.gps.get_speed()
                    return lat, lng, speed
        return None, None, None

    