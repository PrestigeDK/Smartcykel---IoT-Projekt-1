import network
import time
from umqtt.simple import MQTTClient
import dht
from machine import Pin

# ---- WiFi ----
ssid = "Team 3A"
password = "TeamAGP3"

# ---- MQTT Home Assistant ----
mqtt_server = "10.20.0.5"
mqtt_port = 1886                         # <-- Opdateret port
mqtt_user = "TeamAGP3"                # <-- SKRIV DIT MQTT BRUGERNAVN
mqtt_password = "TeamAGP3"              # <-- SKRIV DIT MQTT PASSWORD
mqtt_topic = "homeassistant/sensor/esp32/state"

# ---- DHT11 sensor ----
sensor = dht.DHT11(Pin(0))  # GPIO4

# ---- WiFi connect ----
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(0.5)
print("Connected:", wifi.ifconfig())

# ---- MQTT client ----
client = MQTTClient(
    client_id="ESP32_DHT11",
    server=mqtt_server,
    port=mqtt_port,
    user=mqtt_user,
    password=mqtt_password
)

client.connect()
print("Connected to Home Assistant MQTT on port 1886")

# ---- Loop: send data ----
while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        payload = '{{"temperature": {}, "humidity": {}}}'.format(temp, hum)
        client.publish(mqtt_topic, payload)
        print("Sent:", payload)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
