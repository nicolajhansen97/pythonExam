import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_am2320
import json
from websocket import create_connection

#setup pins
DataLoggerBarcode = '1001'
ipaddress = '10.176.132.150'
WarningLight = 16
WorkingLight = 20
channel = 19
warning = False
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
GPIO.setup(WarningLight, GPIO.OUT)
GPIO.setup(WorkingLight, GPIO.OUT)
i2c = busio.I2C(board.SCL, board.SDA)

#warning Parameter values
MinHumidity = 0
MaxHumidity = 0
MinTemp = 0
MaxTemp = 0


#function measuere
def MeasurePlant():
   data = 'M\n'+DataLoggerBarcode+'\n'
   if GPIO.input(channel):
      data = data + "false\n"
      GPIO.output(WarningLight, True)
      changeWarning(True)
      SendWarning("Plant is to Dry")
   else:
      data = data + "true\n"
      changeWarning(False)
      GPIO.output(WarningLight, False)

   sensor = adafruit_am2320.AM2320(i2c)

   Humidity = sensor.relative_humidity
   Temperature = sensor.temperature
   data = data + 'Humidity: '+format(Humidity)+'%\n'
   data = data + 'Temperature: '+format(Temperature)+'C'
   #check for low or high values
   if Humidity < MinHumidity:
      print("too low Humidity")
      changeWarning(True)
      SendWarning("The plants humidity is to low")
   if Humidity > MaxHumidity:
      print("too high Humidity ")
      changeWarning(True)
      SendWarning("The plants humidity is to high")
   if Temperature < MinTemp:
      print("too low Temp")
      changeWarning(True)
      SendWarning("The plants temperature is to low")
   if Temperature > MaxTemp:
      print("too High Temp")
      changeWarning(True)
      SendWarning("The plants temperature is to high")

   return data

def SendData(Data):
   ws.send(Data)

def changeWarning(bool):
   global warning
   warning = bool

def SendWarning(Warning):
   GPIO.output(WarningLight,True)
   data = 'W\n'+DataLoggerBarcode+'\n'+Warning
   ws.send(data)
   ack = ws.recv()
   if ack == "ack":
      GPIO.output(WarningLight,False)
      changeWarning(False)
   if ack == "deviceBroken":
      print("Error")
      changeWarning(True)

def WantData():
   data = 'D\n'+DataLoggerBarcode+'\nT'
   SendData(data)
   #data saving
   tree = ws.recv()
   test1 = json.loads(tree)
   global MinHumidity
   global MaxHumidity
   global MinTemp
   global MaxTemp
   MinHumidity = test1["HumidityMin"]
   MaxHumidity = test1["HumidityMax"]
   MinTemp = test1["TempMin"]
   MaxTemp = test1["TempMax"]

def checkDevice():
   data = 'C\n'+DataLoggerBarcode+'\nCheck Device'
   SendData(data)
   data2 = ws.recv()
   device = json.loads(data2)
   Working = device["Working"]
   print(Working)
   if Working == False:
      changeWarning(True)
      SendWarning("deviceBroken")
#measuere

count = 0
GPIO.output(WorkingLight, False)
GPIO.output(WarningLight, False)
ws = create_connection("ws://"+ipaddress+":3001/")
WantData()
checkDevice()
while True:
   if count % 2 == 0 and warning==False:
      GPIO.output(WorkingLight, True)
   else:
      GPIO.output(WorkingLight, False)
   if count == 3600: #3600
      checkDevice()
      Data = MeasurePlant()
      SendData(Data)
      count = -1
   time.sleep(1)
   count = count+1

ws.close()