import gpiozero
from time import sleep
led = gpiozero.LED(18)
while True:
	led.on()
	print("1")
	sleep(1)
	led.off
	print("2")
	sleep(1)
	led.on()
	print("1")
	sleep(1)
	led.off
	print("2")
	sleep(1)
