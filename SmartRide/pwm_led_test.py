from machine import Pin, PWM

pin_led_red = 26

led_red_freq = 40
led_red_duty = 512

led_red = PWM(Pin(pin_led_red))

led_red.freq(led_red_freq)
led_red.duty(led_red_duty)


