Setup-guide: Sådan satte jeg vores ThingsBoard- og ESP32-løsning op på Linux Mini-PC.



Dette dokument beskriver, hvordan jeg satte hele vores IoT-kæde op, så ESP32-enheden kan sende GPS-data, få twilight-tider retur via ThingsBoard, og Ubuntu-mini-PC’en automatisk beregner og opdaterer twilight-værdierne hvert 10. minut. Guiden er skrevet som en log over, hvad jeg gjorde, trin for trin.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**1. Opsætning af ThingsBoard device**



1\. Jeg åbnede ThingsBoard i browseren via vores mini-pc:

&nbsp;  http://mini-pc-ip:8080  (fx 10.20.0.4)



2\. Jeg gik til Devices og fandt det device, som vores ESP32 skal bruge.



3\. Under Device Credentials hentede jeg “Device Access Token”.  

&nbsp;  Det token bruges både af ESP’en og af Ubuntu-scriptet.



4\. Jeg sikrede, at ESP’en allerede havde sendt lat/lng som client attributes,

&nbsp;  så Python-scriptet kan hente dem senere.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**2. Placering af Python-script på mini PC**



1\. Jeg lavede en mappe til vores scripts:

&nbsp;  mkdir -p /team3gruppea/desktop/tb-scripts



2\. Jeg gemte filen “sun\_times.py” i denne mappe.



3\. Jeg gjorde scriptet eksekverbart:

&nbsp;  chmod +x sun\_times.py



4\. Scriptet gør følgende:

&nbsp;  - Henter lat/lng fra ThingsBoard (client attributes)

&nbsp;  - Kalder sunrise-sunset API

&nbsp;  - Konverterer civil twilight begin/end til decimal-timer

&nbsp;  - Sender værdierne tilbage til ThingsBoard som client attributes



5\. Jeg testede scriptet manuelt:

&nbsp;  ./sun\_times.py

&nbsp;  Her tjekkede jeg, at værdierne dukkede op i ThingsBoard, hvilket de gjorde.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**3. Opsætning af cron-job på Linux mini PC**



1\. Jeg åbnede crontab:

&nbsp;  crontab -e



2\. Jeg tilføjede dette cron job, så twilight-scriptet kører hvert 10. minut:



&nbsp;  \*/10 \* \* \* \* /usr/bin/env python3 /team3gruppea/desktop/tb-scripts/sun\_times.py >> /team3gruppea/desktop/sun\_times.log 2>\&1



3\. Jeg gemte filen og tjekkede cron-status:

&nbsp;  systemctl status cron



4\. Resultatet:

&nbsp;  Mini-pc’en kører nu automatisk twilight-beregningen med faste intervaller.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**4. Opsætning af ESP32 (boot.py + main.py)**



1\. I ESP32’s boot.py sørgede jeg for, at enheden forbinder til WiFi automatisk

&nbsp;  hver gang den starter. Det betyder, at main.py kan antage, at WiFi allerede virker.



2\. Jeg sørgede for, at secrets.py indeholder:

&nbsp;  - SSID

&nbsp;  - PASSWORD

&nbsp;  - SERVER\_IP\_ADDRESS (mini pc’ens IP)

&nbsp;  - ACCESS\_TOKEN (samme token som Python scriptet bruger)



3\. I main.py skrev jeg logikken:

&nbsp;  - Forbind til ThingsBoard via MQTT

&nbsp;  - Send GPS (telemetry)

&nbsp;  - Request twilight attributes via request\_attributes()

&nbsp;  - Vent på MQTT-svar i op til 10 sekunder

&nbsp;  - Vis output (kun korte beskeder)

&nbsp;  - Gå i deep sleep i 10 minutter



4\. Når ESP’en vågner igen:

&nbsp;  - boot.py kører automatisk WiFi

&nbsp;  - main.py henter twilight og sender GPS igen

&nbsp;  - Enheden går tilbage i deep sleep

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**5. Test**



For at sikre alt virkede, gjorde jeg følgende:



1\. Startede ESP32 og så i shell:

&nbsp;  - WiFi OK

&nbsp;  - ThingsBoard connected

&nbsp;  - GPS sendt

&nbsp;  - Twilight hentet

&nbsp;  - Deep sleep besked



2\. På ThingsBoard:

&nbsp;  - Under telemetry fandt jeg lat/lng

&nbsp;  - Under client attributes så jeg twilight-tiderne opdatere



3\. På Linux mini PC:

&nbsp;  - Jeg kiggede i loggen:

&nbsp;    tail -f ~/sun\_times.log

&nbsp;  - Her kunne jeg se, hvis noget gik galt.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



**6. Noter**



\- ESP’en bruger deep sleep, hvilket holder strømforbruget lavt.

\- Python-scriptet kører uafhængigt af ESP’en, så twilight-data er altid opdateret.

\- MQTT bruges til at sende og modtage attributter uden HTTP-kald fra ESP’en.

\- ThingsBoard fungerer som mellemled og database.

