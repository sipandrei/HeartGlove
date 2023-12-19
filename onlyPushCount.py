
#presupunem accelerometru ADXL345
#folosim libraria adafruit_adxl34x
#folosim picovoice pentru speech recognition https://www.picovoice.ai
import os
import time
import board
import busio
import adafruit_adxl34x
import env
import math


# Variabile accelerometru
i2c = busio.I2C(board.SCL, board.SDA)
accelerometru = adafruit_adxl34x.ADXL345(i2c)

# Variabile acceleratii
oldX = 0
oldY = 0
oldZ = 0
nowX = 0
nowY = 0
nowZ = 0
acX = 0
acY = 0
acZ = 0

# Variabile cu informații despre apăsări
distJos = 0.035 # apasare minima de 3 centimetri jumatate
distSus = 0.055 # apasare maxima de 5 centimetri jumatate
durJos = 95 # cadenta minima de 95 de apasari pe minut
durSus = 105 # cadenta maxima de 105 de apasari pe minut
marjaAcc = 2 # diferența minimă de accelerație de 2 m/s^2 pentru considerarea mișcării -
# este cu minus deoarece în timpul apasarii se merge spre -Z
ultimaDist = 0
ultimaDurata = 0
apasari = 0
apasare = False

# Algoritm verificare apasari
def verificareApasare(accX, accY, accZ):
  global accelerometru,oldX,oldY,oldZ,marjaAcc,apasare,apasari,ultimaDist,ultimaDurata
  if abs(accx) < marjaAcc and abs(accY) < marjaAcc:
    if accZ - oldZ < -marjaAcc: # Verificare miscare doar pe axa Z
      apasare = True
      durata = 0
      sumAcc = 0 # initializare variabile pentru calcularea acceleratiei medie pe apasare
    while apasare == True:
      durata += 1
      sumAcc += abs(oldZ) # actualizare variabile pentru medie
      oldZ = accZ
      accZ = accelerometru.acceleration[2]-9.8 # citim acceleratia noua
      if accZ - oldZ > marjaAcc: # verificare final apasare sau incepere decomprimare
        apasari += 1
        apasare = False # iesire din modul de apasare si incrementare numar apasari
        accMedie = sumAcc / (durata-1)
        durata = 1e-3*durata #schimbarae din ms in s
        ultimaDist = 1/2 * accMedie*(durata)**2 # calculare distanta parcursa pe baza acceleratiei medie
        ultimaDurata = durata # stocare in variabile globale
      time.sleep(1e-3) # se asteapta 1 ms

# Functie citire acceleratii
def citireAcc(accX, accY, accZ):
  global oldX,oldY,oldZ, nowX, nowY, nowZ
  accAcum = accelerometru.acceleration
  oldX = accX
  oldY = accY
  oldZ = accZ
  nowX = accAcum[0]
  nowY = accAcum[1]
  nowZ = accAcum[2]-9.8

# Functie pentru verificare interval
def verificareMarje(contor, marjaJos, marjaSus):
  if contor < marjaJos:
    return -1
  elif contor > marjaSus:
    return 1
  else:
    return 0

# Functie principala output mesaje
def smartPrint(mesaj):
  print(mesaj)

# Functie interpretare apasari
def masterApasari():
  timpStart = time.time()
  while apasari < 30:
    citireAcc(nowX, nowY, nowZ)
    verificareApasare(nowX, nowY, nowZ) # verificam apasari pana ajung la 30
    marjeDist = verificareMarje(ultimaDist,distJos, distSus)
    # interpretare ultima apasare in functie de distanta
    if marjeDist == -1:
      smartPrint("Apasa mai profund!")
    elif marjeDist == 1:
      smartPrint("Apasa mai putin!")
    elif marjeDist == 0:
      smartPrint("Apasare OK")
    if math.floor(time.time()-timpStart) > 60:
      smartPrint("Timp prea mare pentru setul de apasari")
    marjeDurata = verificareMarje(ultimaDurata*60,durJos, durSus)
    # interpretare ultima apasare in functie de durata
    if marjeDurata == -1:
      smartPrint("Apasa mai rapid!")
    elif marjeDurata == 1:
      smartPrint("Apasa mai încet!")
    elif marjeDurata == 0:
      smartPrint("Apasare OK")

# Apelare functii
initialSetup()
prezentareProcedura()
while not semnalStop():
  masterApasari()
  rasuflari()
