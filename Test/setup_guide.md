Setup-guide: Sådan satte vi vores ThingsBoard- og ESP32-løsning op på Linux Mini-PC.



Dette dokument beskriver, hvordan vi satte hele vores IoT-kæde op, så ESP32-enheden kan sende GPS-data, få twilight-tider retur via ThingsBoard, og Ubuntu-mini-PC’en automatisk beregner og opdaterer twilight-værdierne hvert 10. minut. Guiden er skrevet som en log over, hvad vi gjorde, trin for trin.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



1. **Opsætning af Thingsboard**



1. Vi har fulgt denne guide fra thingsboard, til download, opsætning og konfigurering af thingsboard: https://thingsboard.io/docs/user-guide/install/ubuntu/
2. Til konfiguration af thingsboard.conf filen, skal følgende indsættes også: 

\# Networking

export SERVER\_ADDRESS=0.0.0.0

export MQTT\_ENABLED=true

export MQTT\_BIND\_ADDRESS=0.0.0.0

export MQTT\_BIND\_PORT=1886

Dette gøres, så MQTT sættes op til den rigtige port og at der bliver lyttet på alle adresser, altså 0.0.0.0.



\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**2. Opsætning af ThingsBoard device**



1. Gå til /usr/share/thingsboard (Eller anden mappe, man har valgt at downloade thingboard til) for at starte thingsboard, sudo service thingsboard start



2\. Vi åbnede ThingsBoard i browseren via vores mini-pc:

   http://localhost:8080  (eller 10.20.0.4:8080 på en anden pc)



3\. Vi gik til Devices og fandt det device, som vores ESP32 skal bruge.



4\. Under Device Credentials hentede vi “Device Access Token”. Det token, som bruges både af ESP’en og af Ubuntu-scriptet.



5\. Vi sikrede, at ESP’en allerede havde sendt lat/lng som client attributes, så Python-scriptet kan hente dem senere. Hvis ikke, kan man ændre i scriptet og manuelt indsætte værdier i 'shared' attributes. I scriptet vil man så ændre alle 'client' variabler til 'shared'. Husk også at tjekke url'en også.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**3. Placering af Python-script på mini PC**



1\. Vi lavede en mappe til vores scripts:

   mkdir -p /teamagruppe3/tb-scripts



2\. Jeg gemte filen “sun\_times.py” i denne mappe, sudo nano sun\_times.py. Samt jeg lagde scriptet ind, minipc\_tb\_script.py.



3\. Jeg gjorde scriptet eksekverbart:

   chmod +x sun\_times.py



4\. Scriptet gør følgende:

   - Henter lat/lng fra ThingsBoard (client attributes)

   - Kalder sunrise-sunset API

   - Konverterer civil twilight begin/end til decimal-timer

   - Sender værdierne tilbage til ThingsBoard som client attributes



5\. Jeg testede scriptet manuelt:

   ./sun\_times.py

   Her tjekkede jeg, at værdierne dukkede op i ThingsBoard, hvilket de gjorde.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**4. Opsætning af cron-job på Linux mini PC**



1\. Vi åbnede crontab:

   crontab -e



2\. Vi tilføjede dette cron job, så twilight-scriptet kører hvert 10. minut:



   \*/10 \* \* \* \* /usr/bin/env python3 /team3gruppea/tb-scripts/sun\_times.py >> /team3gruppea/sun\_times.log 2>\&1



3\. Vi gemte filen og tjekkede cron-status:

   systemctl status cron



4\. Resultatet:

   Mini-pc’en kører nu automatisk twilight-beregningen med faste intervaller.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**5. Opsætning af ESP32 (boot.py + main.py)**



1\. I ESP32’s boot.py sørgede vi for, at enheden forbinder til WiFi automatisk

   hver gang den starter. Det betyder, at main.py kan antage, at WiFi allerede virker.



2\. Jeg sørgede for, at secrets.py indeholder:

   - SSID

   - PASSWORD

   - SERVER\_IP\_ADDRESS (mini pc’ens IP)

   - ACCESS\_TOKEN (samme token som Python scriptet bruger, til enheden i thingsboard)



3\. I main.py skrev vi logikken:

   - Forbind til ThingsBoard via MQTT

   - Send GPS og andet (telemetry)

   - Request twilight attributes via request\_attributes()

   - Vent på MQTT-svar i op til 10 sekunder

   - Vis output i shell



4\. Når ESP’en vågner igen:

   - boot.py kører automatisk WiFi

   - main.py henter twilight og sender GPS mm. igen

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**6. Test**



For at sikre alt virkede, gjorde vi følgende:



1\. Startede ESP32 og kiggede i shell:

   - WiFi OK

   - ThingsBoard connected

   - Data sendt

   - Twilight hentet



2\. På ThingsBoard:

   - Under telemetry fandt jeg lat/lng

   - Under client attributes så jeg twilight-tiderne opdatere

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



