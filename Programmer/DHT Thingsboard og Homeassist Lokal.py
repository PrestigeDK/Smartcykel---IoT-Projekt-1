import network
import time
from umqtt.simple import MQTTClient
import dht
from machine import Pin

# ---- WiFi ----
ssid = "Team 3A"
password = "TeamAGP3"

# ---- DHT11 ----
sensor = dht.DHT11(Pin(0))

# ---- ThingsBoard MQTT ----
tb_server = "10.20.0.4"
tb_port = 1886
tb_token = "7gatrvuve5mbds9hv6oc"   # Access token

# ---- Home Assistant MQTT ----
ha_server = "10.20.0.5"
ha_port = 1886
ha_user = "TeamAGP3"            # <-- SKRIV DIT MQTT USER
ha_password = "TeamAGP3"          # <-- SKRIV DIT MQTT PASSWORD
ha_topic = "homeassistant/sensor/esp32/state"

# ---- WiFi connnect ----
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(0.5)
print("Connected:", wifi.ifconfig())

# ---- MQTT Clients ----
tb_client = MQTTClient(
    client_id="ESP32_TB",
    server=tb_server,
    port=tb_port,
    user=tb_token,
    password=""
)

ha_client = MQTTClient(
    client_id="ESP32_HA",
    server=ha_server,
    port=ha_port,
    user=ha_user,
    password=ha_password
)

tb_client.connect()
print("Connected to ThingsBoard")

ha_client.connect()
print("Connected to Home Assistant MQTT")


# ---- MAIN LOOP ----
while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        payload = '{{"temperature": {}, "humidity": {}}}'.format(temp, hum)

        # --- send til ThingsBoard ---
        tb_client.publish("v1/devices/me/telemetry", payload)
        print("Sent to ThingsBoard:", payload)

        # --- send til Home Assistant ---
        ha_client.publish(ha_topic, payload)
        print("Sent to Home Assistant:", payload)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
