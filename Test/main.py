import time
import network
import machine
from uthingsboard.client import TBDeviceMqttClient
import secrets

# Hvor længe ESP skal gå i deepsleep mellem hver cyklus (i minutter)
CYCLE_MINUTES = 10

# Globalt dictionary til at lagre twilight-data
twilight = {
    "begin": None,
    "end": None}

def attributes_callback(payload):
    """
    Bliver kaldt automatisk når ThingsBoard sender svar på request_attributes().
    Payload-struktur:
      {
        "client": {
           "civil_twilight_begin_decimal": <float>,
           "civil_twilight_end_decimal": <float>
        }
      }
    """
    client_attrs = payload.get("client", {})

    if "civil_twilight_begin_decimal" in client_attrs:
        twilight["begin"] = round(client_attrs["civil_twilight_begin_decimal"], 2)

    if "civil_twilight_end_decimal" in client_attrs:
        twilight["end"] = round(client_attrs["civil_twilight_end_decimal"], 2)

    print(f"[TB] Twilight --> Begin: {twilight['begin']}  End: {twilight['end']}")


def main():
    # WiFi bør være forbundet af boot.py
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("[WiFi] Fejl: WiFi ikke forbundet.")
        return

    print("[WiFi] Aktiv. IP =", wlan.ifconfig()[0])

    # 1. Forbind til ThingsBoard via MQTT
    print("[TB] Forbinder til ThingsBoard...")
    client = TBDeviceMqttClient(host=secrets.SERVER_IP_ADDRESS,port=1886,access_token=secrets.ACCESS_TOKEN)
    client.connect()
    print("[TB] Forbundet")

    # 2. Send GPS-data til ThingsBoard (gps data er hardcoded for nu)
    gps_data = {"lat": 55.6761, "lng": 12.5683}
    print("[GPS] Sender:", gps_data)
    client.send_telemetry(gps_data)

    # 3. Bed ThingsBoard om twilight-data
    print("[TB] Anmoder om twilight-data...")
    client.request_attributes(client_keys=["civil_twilight_begin_decimal", "civil_twilight_end_decimal"],callback=attributes_callback)

    # 4. Vent på MQTT-svar (max 10 sekunder)
    timeout_s = 10
    start = time.time()
    while time.time() - start < timeout_s:
        client.check_msg()  # nødvendigt for at modtage MQTT-pakker
        if twilight["begin"] is not None:
            break  # vi har modtaget svar
        time.sleep(0.2)

    # 5. Afslut MQTT-forbindelsen
    try:
        client.disconnect()
    except:
        pass

    # 6. Gå i deep sleep i x minutter
    sleep_ms = CYCLE_MINUTES * 60 * 1000
    print(f"[SYS] Deep sleep i {CYCLE_MINUTES} minutter...")
    machine.deepsleep(sleep_ms)


main()