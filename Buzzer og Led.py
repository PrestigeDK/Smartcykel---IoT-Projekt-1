from machine import Pin, PWM
from time import sleep

buzzer = PWM(Pin(14, Pin.OUT))
buzzer.duty(0)

led = Pin(33, Pin.OUT)   
led.off()

def play_tone(buzobj, freq, tone_dur, sil_dur):
    buzobj.duty(512)
    buzobj.freq(freq)
    led.on()
    sleep(tone_dur)

    buzobj.duty(0)
    led.off()
    sleep(sil_dur)
    
play_tone(buzzer, 1000, 0.3, 0.05)
play_tone(buzzer, 1500, 0.3, 0.05)
play_tone(buzzer, 1000, 0.3, 0.05)
play_tone(buzzer, 1500, 0.3, 0.05)
play_tone(buzzer, 1000, 0.3, 0.05)
play_tone(buzzer, 1500, 0.3, 0.05)
play_tone(buzzer, 1000, 0.3, 0.05)
play_tone(buzzer, 1500, 0.3, 0.05)