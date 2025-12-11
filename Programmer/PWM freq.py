#A simple LED and PWM demo program
from machine import Pin,PWM

pin_led_red = 12

led_red_freq = 70
led_red_duty = 256

led_red = PWM(Pin(pin_led_red))

print("LED PWM test program")

led_red.freq(led_red_freq)
led_red.duty(led_red_duty)
