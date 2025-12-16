import time
from uthingsboard.client import TBDeviceMqttClient
import secrets

class ThingsBoardClient:
    def __init__(self):
        self.twilight = {"begin": None, "end": None}
        self.client = TBDeviceMqttClient(host=secrets.SERVER_IP_ADDRESS,port=1886,access_token=secrets.ACCESS_TOKEN)

    def connect(self):
        print("Forbinder til ThingsBoard...")
        self.client.connect()
        print("Forbundet")

    def disconnect(self):
        self.client.disconnect()
        print("Afbrudt forbindelse til ThingsBoard")

    def send_gps(self, lat, lng, speed, course):
        data = {"lat": lat, "lng": lng, "speed": speed, "course": course}
        print("Sender GPS data:", data)
        self.client.send_telemetry(data)
    
    def send_battery(self, pct):
        data = {"battery_pct": round(pct, 2)}
        print("Sender batteri-telemetry (procent):", data)
        self.client.send_telemetry(data)
        
    def send_temperature(self, temperature_c):
        data = {"temperature_c": round(temperature_c, 1)}
        self.client.send_telemetry(data)

    def attributes_callback(self, payload):
        client_attrs = payload.get("client", {})

        if "civil_twilight_begin_decimal" in client_attrs:
            self.twilight["begin"] = round(client_attrs["civil_twilight_begin_decimal"], 2)
        if "civil_twilight_end_decimal" in client_attrs:
            self.twilight["end"] = round(client_attrs["civil_twilight_end_decimal"], 2)

        print(f"Twilight --> Begin: {self.twilight['begin']}  "
              f"End: {self.twilight['end']}")

    def get_twilight(self, timeout_s=10):
        self.twilight["begin"] = None
        self.twilight["end"] = None

        print("Anmoder om twilight-data...")
        self.client.request_attributes(client_keys=["civil_twilight_begin_decimal","civil_twilight_end_decimal"],callback=self.attributes_callback)

        start = time.time()
        while time.time() - start < timeout_s:
            self.client.check_msg()
            if self.twilight["begin"] is not None:
                break
            time.sleep(0.2)

        return self.twilight