#!/usr/bin/env python3
import requests

# Konfiguration
# Scriptet kører på samme maskine som ThingsBoard:
TB_URL = "http://localhost:8080"

# Device access token (SAMME som på ESP32 / ThingsBoard device)
TB_TOKEN = "DEVICE_TOKEN_HER"

SUN_API_URL = "https://api.sunrise-sunset.org/json"


def tid_til_decimal(tid_str: str) -> float:
    """
    Konverterer tid i formatet 'TT:MM:SS AM/PM' til decimal-timer.
    Eksempel: '6:39:00 AM' -> 6.65
    """
    tid_split, ampm = tid_str.split()
    t, m, s = map(int, tid_split.split(":"))

    if ampm == "PM" and t != 12:
        t += 12
    if ampm == "AM" and t == 12:
        t = 0
        
    return t + m / 60.0  # sekunder ignoreres


def get_lat_lng_from_tb():
    """
    Henter lat/lng fra ThingsBoard client attributes.
    Forventer at ESP32 tidligere har sendt 'lat' og 'lng'.
    """
    url = f"{TB_URL}/api/v1/{TB_TOKEN}/attributes?clientKeys=lat,lng"
    r = requests.get(url, timeout=10)
    r.raise_for_status()

    data = r.json()
    client = data.get("client", {})

    if "lat" not in client or "lng" not in client:
        raise RuntimeError("Fejl: lat/lng findes ikke i client attributes.")

    return float(client["lat"]), float(client["lng"])


def hent_sun_times(lat: float, lng: float):
    """
    Kalder sunrise-sunset API'et og henter civil_twilight_begin/end.
    """
    params = {
        "lat": lat,
        "lng": lng,
        "formatted": 1  # giver '6:39:00 AM' format
    }
    r = requests.get(SUN_API_URL, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()
    res = data["results"]
    return res["civil_twilight_begin"], res["civil_twilight_end"]


def send_to_thingsboard(begin_dec: float, end_dec: float):
    """
    Sender twilight-tiderne tilbage til ThingsBoard som client attributes.
    """
    url = f"{TB_URL}/api/v1/{TB_TOKEN}/attributes"
    payload = {
        "civil_twilight_begin_decimal": begin_dec,
        "civil_twilight_end_decimal": end_dec
    }
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.text


def main():
    print("=== Twilight updater start ===")

    # 1) Hent GPS fra ThingsBoard
    print("Henter GPS koordinater fra ThingsBoard...")
    lat, lng = get_lat_lng_from_tb()
    print(f"Lat: {lat} | Lng: {lng}")

    # 2) Hent civil twilight fra API
    print("Henter civil twilight tider fra API...")
    solop, solned = hent_sun_times(lat, lng)
    print("Rå API:", solop, "/", solned)

    # 3) Konverter til decimal-tid
    solop_dec = tid_til_decimal(solop)
    solned_dec = tid_til_decimal(solned)
    print(f"Decimal: begin={solop_dec:.3f}  end={solned_dec:.3f}")

    # 4) Send til ThingsBoard
    print("Sender twilight-decimaler til ThingsBoard...")
    resp = send_to_thingsboard(solop_dec, solned_dec)
    print("Success:", resp)

    print("=== Twilight updater færdig ===")


if __name__ == "__main__":
    main()