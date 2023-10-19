#presupunem accelerometru ADXL345

import time
import board
import busio
import adafruit_adxl34x

i2c = busio.I2C(board.SCL, board.SDA)
accelerometru = adafruit_adxl34x.ADXL345(i2c)

oldX = 0
oldY = 0
oldZ = 0
nowX = 0
nowY = 0
nowZ = 0
distJos = 0.035 #apasare minima de 3 centimetri jumatate
distSus = 0.055 #apasare maxima de 5 centimetri jumatate
durJos = 95 #cadenta minima de 95 de apasari pe minut
durSus = 105 #cadenta maxima de 105 de apasari pe minut
marjaAcc = 2
ultimaDist = 0
ultimaDurata = 0
apasari = 0
apasare = False

def verificareApasare(accX, accY, accZ):
  if abs(accx - oldX) < marjaAcc and abs(accY - oldY) < marjaAcc:
    if accZ - oldZ > marjaAcc:
      apasare = True
    durata = 0
    sumAcc = 0
    while apasare == True:
      durata += 1
      sumAcc += oldZ
      citireAcc(accX, accY, accZ)
      if accZ - oldZ < -marjaAcc:
        apasari += 1
        apasare = False
        accMedie = sumAcc / durata
        durata = 1e-3*durata #schimbarae din ms in s
        ultimaDist = 1/2 * (accMedie*durata)**2
        ultimaDurata = durata
      time.sleep(1e-3)

def citireAcc(accX, accY, accZ):
  accAcum = accelerometru.acceleration
  oldX = accX
  oldY = accY
  oldZ = accZ
  accX = accAcum[0]
  accY = accAcum[1]
  accZ = accAcum[2]

def verificareMarje(contor, marjaJos, marjaSus):
  if contor < marjaJos:
    return -1
  elif contor > marjaSus:
    return 1
  else:
    return 0

def smartPrint(mesaj):
  print(mesaj)

def masterApasari():
  if apasari < 30:
    citireAcc(nowX, nowY, nowZ)
    verificareApasare(nowX, nowY, nowZ)
    match verificareMarje(ultimaDist, distJos, distSus):
      case -1:
        smartPrint("Apasa mai profund!")
      case 1:
        smartPrint("Apasa mai putin!")
      case 0:
        smartPrint("Apasare OK")

    match verificareMarje(ultimaDurata*60, durJos, durSus):
      case -1:
        smartPrint("Apasa mai rapid!")
      case 1:
        smartPrint("Apasa mai încet!")
      case 0:
        smartPrint("Apasare OK")

def dateVictima():
  print("waiting for voice recognition")

def prezentareProcedura():
  print("to implement screen")

def semnalStop():
  return False

dateVictima()
prezentareProcedura()
while semnalStop():
  masterApasari()
  rasuflari()
