# Disse bruges til timing og wifi
import time
import network
from machine import I2C, Pin

# Importere vores klasser
from gps import GpsReader
from tb_klient import ThingsBoardClient
from bremselys import BremselysStyring
from batteri import Battery

# Hvor ofte vi opdatere GPS/Twilight fra ThingsBoard + batteri/LCD
TB_UPDATE_MINUTES = 5
BATTERY_UPDATE_SECONDS = 5

i2c = I2C(0, scl=Pin(18), sda=Pin(19))

# Hovedfunktionen
def main():
    # 1) WiFi (Ordnet af boot.py)
    # Hvis det ikke er ordnet er boot, smider den en fejl og stopper programmet
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("Fejl: WiFi ikke forbundet.")
        return
    print("WiFi Forbundet.")

    # 2) Opret objekter
    # Her opretter vi objekter af vores klasser vi har lavet, så de senere i programmet kan blive kaldt
    gps = GpsReader()
    tb = ThingsBoardClient()
    bremselys = BremselysStyring(i2c)
    battery = Battery(i2c)

    # 3) Forbind til ThingsBoard via MQTT og tb-klient
    # For at kunne sende og hente data gennem thingsboard, skal forbindelse oprettes, som sker via tb-klienten
    tb.connect()

    # 4) Første GPS + twilight-opdatering
    # Enten bliver lat, lng & speed returneret eller None, hvis data f.eks. mangler
    print("Forsøger at hente GPS data...")
    lat, lng, speed = gps.get_data(timeout_s=10)

    # Her sender vi kun data til thingsboard hvis der er data, altså omvendt af None
    if lat is not None and lng is not None:
        tb.send_gps(lat, lng, speed)
        
        # Vi venter på at thingsboard sender twilight data
        twilight = tb.get_twilight(timeout_s=10)
        print("Twilight data hentet:", twilight)
        
        # Her får vi altså vores twilight_begin og twilight_end data, gemmer dem i bremselys,
        # som senere bruges til at afgøre om det er dag/nat
        if twilight is not None:
            begin = twilight.get("begin")
            end = twilight.get("end")
            if begin is not None and end is not None:
                bremselys.set_twilight(begin, end)
                print(f"Twilight sat til: begin={begin}, end={end}")
                
    # Hvis vi igen får en fejl, smider vi en fejl-besked i shell
    # Det kunne være ugyldig data, indtil vi har fået forbindelse til en satelit
    else:
        print("Ingen gyldig GPS-position, springer TB-opdatering over.")

    # 5) Hovedloop:
    # Kører bremselys.step() hurtigt
    # Opdaterer GPS/Twilight sjældent, det gøres for at spare på strøm
    
    # Dette holder øje med, hvornår sidste thingsboard opdatering skete
    last_battery_update = time.time()
    last_tb_update = time.time()
    tb_update_interval = TB_UPDATE_MINUTES * 60  # Minutter omregnes til sekunder
    
    # Her kører vores bremselys logik: Læse mpu, find ax, tjekker bremsning, tjekke dag/nat og sætte farve
    while True:
        # 5.1) Opdater bremselys hele tiden
        bremselys.step()

        # 5.2) Hvert x minutter, sender vi GPS data og henter ny twilight data
        now = time.time()
        
        if now - last_battery_update >= BATTERY_UPDATE_SECONDS:
            # Opdatere batteri interval
            print("TB-opdateringsvindue...")
            battery.step()
            last_battery_update = now
        
        if now - last_tb_update >= tb_update_interval:
            # Opdatere GPS & twilight hvert interval
            lat, lng, speed = gps.get_data(timeout_s=10)
            
            if lat is not None and lng is not None:
                # Hvis GPS er validt
                tb.send_gps(lat, lng, speed)
                twilight = tb.get_twilight(timeout_s=10)
                print("Twilight data hentet:", twilight)
                
                # Hvis twilight er validt
                if twilight is not None:
                    begin = twilight.get("begin")
                    end = twilight.get("end")
                    
                    if begin is not None and end is not None:
                        bremselys.set_twilight(begin, end)
                        print(f"Twilight opdateret: begin={begin}, end={end}")
                        
            else:
                print("Ingen gyldig GPS-position, springer TB-opdatering over.")
                
                u_bat = battery.read_voltage()
                pct = battery.get_pct(u_bat)
                tb.send_battery(pct)
                
            last_tb_update = now
            
        # Denne pause er for ikke at presse ESP'en for meget og spare på cpu'en     
        time.sleep(0.1)

# Dette starter så programmet vi har lavet ovenover
if __name__ == "__main__":
    main()
