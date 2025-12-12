import network
import time
from umqtt.simple import MQTTClient
import dht
from machine import Pin

# ---- WiFi ----
ssid = "Team 3A"
password = "TeamAGP3"

# ---- ThingsBoard ----
mqtt_server = "10.20.0.4"
mqtt_port = 1886
access_token = "7gatrvuve5mbds9hv6oc"

# ---- DHT11 sensor ----
dht_pin = Pin(0)              # GPIO4, skift hvis din sensor sidder et andet sted
sensor = dht.DHT11(dht_pin)

# ---- WiFi connect ----
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting WiFi...")
while not wifi.isconnected():
    time.sleep(0.5)
print("Connected:", wifi.ifconfig())

# ---- MQTT client ----
client = MQTTClient(
    client_id="ESP32_DHT11",
    server=mqtt_server,
    port=mqtt_port,
    user=access_token,   # ThingsBoard bruger access token som MQTT-username
    password=""
)

client.connect()
print("Connected to ThingsBoard")

# ---- Loop: send data hver 5 sek ----
while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        payload = '{{"temperature": {}, "humidity": {}}}'.format(temp, hum)
        client.publish("v1/devices/me/telemetry", payload)

        print("Sent:", payload)
    except Exception as e:
        print("Sensor/MQTT error:", e)

    time.sleep(5)
