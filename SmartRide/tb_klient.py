import time
from uthingsboard.client import TBDeviceMqttClient
import secrets

class ThingsBoardClient:
    """
    Klasse omkring TBDeviceMqttClient.
    Håndterer:
      - connect/disconnect
      - sende GPS-telemetry
      - hente twilight-attributes
    """

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

    def send_gps(self, lat, lng, speed):
        data = {"lat": lat, "lng": lng, "speed": speed}
        print("Sender GPS data:", data)
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
        """
        Sender en attributes-request til ThingsBoard og venter op til timeout_s
        på svar. Returnerer et dict med 'begin' og 'end' (kan være none hvis
        der ikke kommer svar i tide).
        """
        # Reset værdier
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