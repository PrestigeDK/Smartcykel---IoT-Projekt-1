import requests
import json

respons_data = requests.get(url='https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400')
samlet_data = respons_data.json()

solopgang_data = samlet_data['results']['civil_twilight_begin']
solnedgang_data = samlet_data['results']['civil_twilight_end']

def tid_til_decimal(tid_str):
    tid_split, ampm = tid_str.split()
    t, m, s = map(int, tid_split.split(":"))

    if ampm == "PM" and t != 12:
        t += 12
    if ampm == "AM" and t == 12:
        t = 0

    return t + m / 60  # Dette ignorere sekunder, da vi ikke skal bruge dem til noget.

# Konverter API tider
solopgang_float = tid_til_decimal(solopgang_data)
solnedgang_float = tid_til_decimal(solnedgang_data)

print("Solopgang decimal:", solopgang_float)
print("Solnedgang decimal:", solnedgang_float)

