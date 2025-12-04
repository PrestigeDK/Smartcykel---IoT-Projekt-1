# my_api.py
import requests
import json

class Solop_Solned:
    def __init__(self, url):
        self.url = url
        
    def data_fra_api(self):
        res = requests.get(self.url)

        print('STATUS CODE', res.status_code)
        print('Text version', res.text)
        print('JSON version', res.json())

        print('Pretty-ish JSON',
              json.dumps(res.json(), separators=('\n', ': ')))

# Dette sikrer, at koden nedenfor kun kører, når filen køres direkte

if __name__ == "__main__":
    sol = Solop_Solned('https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400')
    sol.data_fra_api()


