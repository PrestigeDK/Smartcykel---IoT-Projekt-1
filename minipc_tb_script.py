#!/usr/bin/env python3
import requests

TB_URL = "http://localhost:8080"
TB_TOKEN = ""
SUN_API_URL = "https://api.sunrise-sunset.org/json"


# Funktion som laver tid fra api'en om til decimal, så vi bedre kan regne med det
def tid_til_decimal(tid_str):
    tid_split, ampm = tid_str.split()
    t, m, s = map(int, tid_split.split(":"))

    if ampm == "PM" and t != 12:
        t += 12
    if ampm == "AM" and t == 12:
        t = 0

    return t + m / 60  # Ignorer sekunder, da vi ikke skal bruge dem


def get_lat_lng_from_tb(): # Henter lat & lng fra device client attributes.
    url = f"{TB_URL}/api/v1/{TB_TOKEN}/attributes?sharedKeys=lat,lng"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()

    shared = data.get("shared", {})
    if "lat" not in shared or "lng" not in shared:
        raise RuntimeError("lat/lng ikke fundet i shared attributes")

    lat = float(shared["lat"])
    lng = float(shared["lng"])
    return lat, lng


def get_sun_times(lat, lng):
    params = {
        "lat": lat,
        "lng": lng,
        "formatted": 1  # AM/PM format, passer til tid_til_decimal
    }
    r = requests.get(SUN_API_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    if data.get("status") != "OK":
        raise RuntimeError(f"Sun API error: {data.get('status')}")

    res = data["results"]
    solopgang = res["civil_twilight_begin"]
    solnedgang = res["civil_twilight_end"]
    return solopgang, solnedgang


def send_to_thingsboard(begin_dec, end_dec): # Gemmer resultaterne som shared attributes, så enheden kan læse dem som "system data"
    url = f"{TB_URL}/api/v1/{TB_TOKEN}/attributes"
    payload = {
        "civil_twilight_begin_decimal": begin_dec,
        "civil_twilight_end_decimal": end_dec
    }
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.text


def main():
    print("Henter lat/lng fra ThingsBoard...")
    lat, lng = get_lat_lng_from_tb()
    print(f"Lat: {lat}, Lng: {lng}")

    print("Henter sol tider fra API...")
    solopgang_str, solnedgang_str = get_sun_times(lat, lng)
    print("API tider:", solopgang_str, solnedgang_str)

    # Bruger vores konvertering
    solopgang_dec = tid_til_decimal(solopgang_str)
    solnedgang_dec = tid_til_decimal(solnedgang_str)
    print("Decimal:", solopgang_dec, solnedgang_dec)

    print("Sender til ThingsBoard (shared attributes)...")
    resp = send_to_thingsboard(solopgang_dec, solnedgang_dec)
    print("Færdig:", resp)


if __name__ == "__main__":
    main()
