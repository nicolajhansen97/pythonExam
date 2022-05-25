import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_am2320

#setup pins
channel = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
i2c = busio.I2C(board.SCL, board.SDA)

#measuere

while True:
   time.sleep(2)
   if GPIO.input(channel):
      print("No water")
   else:
      print("Water")

   sensor = adafruit_am2320.AM2320(i2c)
   print('Humidity: {0}%'.format(sensor.relative_humidity))
   print('Temperature: {0}C'.format(sensor.temperature))

#output
