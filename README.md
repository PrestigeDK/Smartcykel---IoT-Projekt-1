# Smartcykel — IoT Projekt #1

**Denne repository indeholder al kode og dokumentation for vores IoT-projekt "Smartcykel".**

## Om projektet

Smartcykel-projektet har til formål at udvikle en IoT-løsning, der kan monitorere og forbedre cykling gennem forskellige sensorer og databehandling. Systemet indsamler relevante data fra cyklen og sender disse til en server for yderligere analyse.

## Funktionalitet

- Opsamling af sensor-data (fx hastighed, temperatur, GPS m.m.)
- Dataoverførsel til skyen/server via MQTT eller anden protokol
- Visualisering af data (dashboard/webapp)
- Mulighed for notifikationer/alarmer ved uregelmæssigheder
- Lagring af historiske data

## Teknologier

- **Python** _(100%)_ bruges til al kode i projektet – både indsamling, behandling og kommunikation med server.
- IoT-platform: Typisk Raspberry Pi eller lignende hardware
- Sensortyper: _(uddyb selv: f.eks. DHT11, GPS-modul, Hall-effect sensor etc.)_
- Kommunikation: MQTT-protokol, REST API eller lignende
