from machine import Pin, I2C, UART
from time import sleep, time
from mpu6050 import MPU6050
import network
import urequests
import secrets

# -----------------------------
# KONFIGURATION
# -----------------------------
THINGSBOARD_URL = secrets.SERVER_IP_ADDRESS

STILL_THRESHOLD = 0.05
MOVEMENT_THRESHOLD = 0.15
STILL_TIME_REQUIRED = 180     # 3 minutter

# Bremse-lys threshold
BRAKE_THRESHOLD = -0.5

# -----------------------------
# MPU6050
# -----------------------------
i2c = I2C(0, scl=Pin(18), sda=Pin(19))
mpu = MPU6050(i2c)

# -----------------------------
# Bremse-lys
# -----------------------------
bremse_lys = Pin(12, Pin.OUT)

# -----------------------------
# KNAP PÅ PIN 4  ← NYT
# -----------------------------
knap = Pin(4, Pin.IN, Pin.PULL_UP)  # HIGH = ON, LOW = OFF

# -----------------------------
# GPS
# -----------------------------
gps_uart = UART(1, baudrate=9600, tx=17, rx=16)

def read_gps():
    line = gps_uart.readline()
    if line is None:
        return None, None
    try:
        parts = line.decode().split(',')
        if parts[0] == "$GPRMC" and parts[2] == 'A':
            lat = float(parts[3])
            lon = float(parts[5])
            return lat, lon
    except:
        pass
    return None, None

# -----------------------------
# STATE MACHINE
# -----------------------------
state = "MOVING"
last_movement_time = time()

while True:

    # Læs knapstatus (1 = aktiv, 0 = slukket)   ← NYT
    system_on = (knap.value() == 1)

    vals = mpu.get_values()
    ax = vals['acceleration x'] / 16384
    ay = vals['acceleration y'] / 16384
    az = vals['acceleration z'] / 16384

    # -----------------------------
    # Bremse-lys (kører altid)
    # -----------------------------
    if ax < BRAKE_THRESHOLD:
        bremse_lys.on()
    else:
        bremse_lys.off()

    # -----------------------------
    # Hvis knappen er OFF → stop alt tyveri-detektion
    # -----------------------------
    if not system_on:
        print("System SLUKKET – kun bremselys aktivt")
        sleep(0.3)
        continue   # spring resten over

    # -----------------------------
    # Bevægelsesdetektion
    # -----------------------------
    total_acc = abs(ax) + abs(ay) + abs(az - 1.0)

    if total_acc > MOVEMENT_THRESHOLD:
        last_movement_time = time()

    # -------------------------------------
    # STATE: CYKLEN HAR STÅET STILLE I 3 MIN
    # -------------------------------------
    if state == "MOVING" and (time() - last_movement_time > STILL_TIME_REQUIRED):
        print("Cyklen er nu stille – tyveri-overvågning aktiv")
        state = "IDLE"

    # -------------------------------------
    # STATE: CYKLEN BEGYNDER AT BEVÆGE SIG EFTER STILSTAND
    # -------------------------------------
    if state == "IDLE" and total_acc > MOVEMENT_THRESHOLD:
        print("⚠️ MULIGT TYVERI! CYKLEN ER I BEVÆGELSE! ⚠️")

        lat, lon = read_gps()
        print("GPS:", lat, lon)

        payload = {"theft_alert": True, "lat": lat, "lon": lon}
        try:
            r = urequests.post(THINGSBOARD_URL, json=payload)
            r.close()
        except:
            print("Fejl: Kunne ikke sende til ThingsBoard")

        state = "MOVING"

    sleep(0.2) 
