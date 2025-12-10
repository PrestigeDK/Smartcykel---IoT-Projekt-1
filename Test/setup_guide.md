Setup-guide: Sådan satte jeg vores ThingsBoard- og ESP32-løsning op på Linux Mini-PC.



Dette dokument beskriver, hvordan jeg satte hele vores IoT-kæde op, så ESP32-enheden kan sende GPS-data, få twilight-tider retur via ThingsBoard, og Ubuntu-mini-PC’en automatisk beregner og opdaterer twilight-værdierne hvert 10. minut. Guiden er skrevet som en log over, hvad jeg gjorde, trin for trin.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**1. Opsætning af ThingsBoard device**



1. Gå til /usr/share/thingsboard for at starte thingsboard, sudo service thingsboard start



2\. Jeg åbnede ThingsBoard i browseren via vores mini-pc:

   http://localhost:8080  (eller 10.20.0.4:8080 på en anden pc)



3\. Jeg gik til Devices og fandt det device, som vores ESP32 skal bruge.



4\. Under Device Credentials hentede jeg “Device Access Token”.

   Det token bruges både af ESP’en og af Ubuntu-scriptet.



5\. Jeg sikrede, at ESP’en allerede havde sendt lat/lng som client attributes,

   så Python-scriptet kan hente dem senere. Hvis ikke, kan man ændre i scriptet og manuelt indsætte værdier i 'shared' attributes. I scriptet vil man så ændre alle 'client' til 'shared'. Husk også at tjekke url'en.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**2. Placering af Python-script på mini PC**



1\. Jeg lavede en mappe til vores scripts:

   mkdir -p /team3gruppea/tb-scripts



2\. Jeg gemte filen “sun\_times.py” i denne mappe, sudo nano sun\_times.py. Samt jeg lagde scriptet ind.



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



**3. Opsætning af cron-job på Linux mini PC**



1\. Jeg åbnede crontab:

   crontab -e



2\. Jeg tilføjede dette cron job, så twilight-scriptet kører hvert 10. minut:



   \*/10 \* \* \* \* /usr/bin/env python3 /team3gruppea/tb-scripts/sun\_times.py >> /team3gruppea/sun\_times.log 2>\&1



3\. Jeg gemte filen og tjekkede cron-status:

   systemctl status cron



4\. Resultatet:

   Mini-pc’en kører nu automatisk twilight-beregningen med faste intervaller.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**4. Opsætning af ESP32 (boot.py + main.py)**



1\. I ESP32’s boot.py sørgede jeg for, at enheden forbinder til WiFi automatisk

   hver gang den starter. Det betyder, at main.py kan antage, at WiFi allerede virker.



2\. Jeg sørgede for, at secrets.py indeholder:

   - SSID

   - PASSWORD

   - SERVER\_IP\_ADDRESS (mini pc’ens IP)

   - ACCESS\_TOKEN (samme token som Python scriptet bruger)



3\. I main.py skrev jeg logikken:

   - Forbind til ThingsBoard via MQTT

   - Send GPS (telemetry)

   - Request twilight attributes via request\_attributes()

   - Vent på MQTT-svar i op til 10 sekunder

   - Vis output (kun korte beskeder)

   - Gå i deep sleep i 10 minutter



4\. Når ESP’en vågner igen:

   - boot.py kører automatisk WiFi

   - main.py henter twilight og sender GPS igen

   - Enheden går tilbage i deep sleep

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**5. Test**



For at sikre alt virkede, gjorde jeg følgende:



1\. Startede ESP32 og så i shell:

   - WiFi OK

   - ThingsBoard connected

   - GPS sendt

   - Twilight hentet

   - Deep sleep besked



2\. På ThingsBoard:

   - Under telemetry fandt jeg lat/lng

   - Under client attributes så jeg twilight-tiderne opdatere



3\. På Linux mini PC:

   - Jeg kiggede i loggen:

     tail -f ~/sun\_times.log

   - Her kunne jeg se, hvis noget gik galt.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**6. Noter**



\- ESP’en bruger deep sleep, hvilket holder strømforbruget lavt.

\- Python-scriptet kører uafhængigt af ESP’en, så twilight-data er altid opdateret.

\- MQTT bruges til at sende og modtage attributter uden HTTP-kald fra ESP’en.

\- ThingsBoard fungerer som mellemled og database.

