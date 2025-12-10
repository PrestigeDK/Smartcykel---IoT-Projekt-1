#import ting
from machine import Pin, PWM
from time import sleep

#lav buzzer object
buzzer = PWM(Pin(14,Pin.OUT),duty=0)

buzzer.duty (512)
buzzer.freq(440)
sleep(1)
buzzer.duty(0)
sleep(0.1)
buzzer.duty(512)
buzzer.freq(1319)
sleep(1)
buzzer.duty(0)

def play_tone(buzobj,freq,tone_dur,sil_dur):
    buzobj.duty(512)
    buzobj.freq(freq)
    sleep(tone_duration)
    pwm_objekt.duty(0)
    sleep(silence_duration)
    
    play_tone(buzzer,1319,1,0.1)