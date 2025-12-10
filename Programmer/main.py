from uthingsboard.client import TBDeviceMqttClient
from time import sleep
from sys import exit
import gc
import secrets
from machine import Pin, PWM
from lcd_api import LcdApi
from gpio_lcd import GpioLcd
from solop_solned import Solop_Solned


lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32), d6_pin=Pin(21), d7_pin=Pin(22),
              num_lines=4, num_columns=20)

BUZZER_PIN = 14
buzzer_pin = Pin(BUZZER_PIN, Pin.OUT)
buzzer = PWM(buzzer_pin)
buzzer.duty(0)


led1 = Pin(26, Pin.OUT)
""""custom_chr = bytearray([0b01110,
  0b01010,
  0b01010,
  0b01010,
  0b01010,
  0b01010,
  0b11011,
  0b11011])"""

"""lcd.putstr('Hey Hey')
lcd.move_to(0, 1)
lcd.putstr(' Lav big brain moves i dag')"""

# the handler callback that gets called when there is a RPC request from the server
def handler(req_id, method, params):
    """handler callback to recieve RPC from server """
     # handler signature is callback(req_id, method, params)
    print(f'Response {req_id}: {method}, params {params}')
    print(params, "params type:", type(params))
    try:
        # check if the method is "toggle_led1" (needs to be configured on thingsboard dashboard)
        if method == "toggle_led1":
            # check if the value is is "led1 on"
            if params == True:
                print("led1 on")
                led1.on()
            else:
                print("led1 off")
                led1.off()
                
        if method == "toggle_buzzer":
            if params == True:
                print("buzzer is on")
                buzzer.duty(250)
            else:
                print("buzzer is on")
                buzzer.duty(0)
                
        # check if command is send from RPC remote shell widget   
        if method == "sendCommand":
            lcd.clear()
            lcd.putstr(params.get("command"))
            
    

    except TypeError as e:
        print(e)

# see more about ThingsBoard RPC at the documentation:
# https://thingsboard.io/docs/user-guide/rpc/
        
# See examples for more authentication options
# https://github.com/thingsboard/thingsboard-micropython-client-sdk/
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token = secrets.ACCESS_TOKEN)


# Connecting to ThingsBoard
client.connect()
print("connected to thingsboard, starting to send and receive data")
while True:
    try:
        print(f"free memory: {gc.mem_free()}")
        # monitor and free memory
        if gc.mem_free() < 2000:
            print("Garbage collected!")
            gc.collect()
        
        # uncomment for sending telemetry from device to server       
        
        #telemetry = {}
        #client.send_telemetry(telemetry)
        
        #callback to get server RPC requests
        client.set_server_side_rpc_request_handler(handler) 
        
        # Checking for incoming subscriptions or RPC call requests (non-blocking)
        client.check_msg()
        sleep(3) # blocking delay
    except KeyboardInterrupt:
        print("Disconnected!")
        # Disconnecting from ThingsBoard
        client.disconnect()
        exit()


