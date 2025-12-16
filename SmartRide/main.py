import time
import network
from machine import I2C, Pin
from gps import GpsReader
from tb_klient import ThingsBoardClient
from bremselys import BremselysStyring
from batteri import Battery

TB_UPDATE_MINUTES = 2
BATTERY_UPDATE_SECONDS = 30
GPS_CHECK_SECONDS = 30
STATIONARY_SECONDS = 20
MOVE_THRESHOLD_M = 2

i2c = I2C(0, scl=Pin(18), sda=Pin(19))

def main():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("Fejl: WiFi ikke forbundet.")
        return

    gps = GpsReader()
    tb = ThingsBoardClient()
    bremselys = BremselysStyring(i2c)
    battery = Battery(i2c)

    tb.connect()

    gps_valid, lat, lng, speed, course = gps.read_valid(10)

    had_fix = gps_valid

    if gps_valid:
        tb.send_gps(lat, lng, speed, course)
        battery.set_gps(lat, lng, course, speed)

    twilight = tb.get_twilight(timeout_s=10)
    if twilight is not None:
        begin = twilight.get("begin")
        end = twilight.get("end")
        if begin is not None and end is not None:
            bremselys.set_twilight(begin, end)

    last_battery_update = time.time()
    last_tb_update = time.time()
    tb_update_interval = TB_UPDATE_MINUTES * 60
    
    last_gps_check = time.time()
    
    last_lat = None
    last_lng = None
    
    last_move_time = time.time()
    
    theft_armed = False
    theft_alert = False
    
    theft_gps_seconds = 10
    last_theft_gps_send = 0

    while True:
        bremselys.step()

        now = time.time()
        
        if theft_alert and (now - last_theft_gps_send >= theft_gps_seconds):
            gps_valid, lat, lng, speed, course = gps.read_valid(3)
            
            if gps_valid:
                had_fix = True
                tb.send_gps(lat, lng, speed, course)

            last_theft_gps_send = now
        
        
        if now - last_gps_check >= GPS_CHECK_SECONDS:
            gps_valid, lat, lng, speed, course = gps.read_valid(3)

            if gps_valid:
                had_fix = True
                battery.set_gps(lat, lng, course, speed)

                if last_lat is None and last_lng is None:
                    last_lat, last_lng = lat, lng
                    last_move_time = now
                else:
                    moved = False
                    distance_m = gps.haversine(last_lat, last_lng, lat, lng)
                    moved = distance_m >= MOVE_THRESHOLD_M

                    last_lat, last_lng = lat, lng

                    if moved:
                        last_move_time = now
                        if theft_armed and not theft_alert:
                            theft_alert = True
                            theft_armed = False
                            tb.client.send_telemetry({"theft_alert": 1})
                    else:
                        if had_fix and (now - last_move_time) >= STATIONARY_SECONDS and not theft_alert:

                            theft_armed = True

            last_gps_check = now
                      
        if now - last_battery_update >= BATTERY_UPDATE_SECONDS:
            battery.step()
            last_battery_update = now

        if now - last_tb_update >= tb_update_interval:
            gps_valid, lat, lng, speed, course = gps.read_valid(3)

            if gps_valid:
                had_fix = True
                tb.send_gps(lat, lng, speed, course)
                battery.set_gps(lat, lng, course, speed)

                twilight = tb.get_twilight(timeout_s=10)
                if twilight is not None:
                    begin = twilight.get("begin")
                    end = twilight.get("end")
                    if begin is not None and end is not None:
                        bremselys.set_twilight(begin, end)

            u_bat = battery.read_voltage()
            pct = battery.get_pct(u_bat)
            tb.send_battery(pct)
            
            temperature_c = battery.read_temperature()
            tb.send_temperature(temperature_c)

            last_tb_update = now

        time.sleep(0.1)

if __name__ == "__main__":
    main()