import time
import board
import busio
import adafruit_adxl34x

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
accMedie = 0

def verificareApasare(accX, accY, accZ):
  global accMedie,oldX,oldY,oldZ,marjaAcc,apasare,apasari,ultimaDist,ultimaDurata
  if abs(accX) < marjaAcc+20 and abs(accY) < marjaAcc+20:
    if accZ > marjaAcc: # Verificare miscare doar pe axa Z
      apasare = True
      durata = 0
      sumAcc = 0 # initializare variabile pentru calcularea acceleratiei medie pe apasare
    while apasare == True:
      durata += 1
      sumAcc += abs(oldZ) # actualizare variabile pentru medie
      oldZ = accZ
      accZ = accelerometru.acceleration[2]-9.8 # citim acceleratia noua
      print(accZ)
      if accZ < -marjaAcc and durata > 15: # verificare final apasare sau incepere decomprimare
        print(f"suma acc {sumAcc}")
        apasari += 1
        apasare = False # iesire din modul de apasare si incrementare numar apasari
       	if durata != 1:
          accMedie = sumAcc / (durata-1)
        else:
          accMedie = sumAcc / durata
        print(f"ultima acc {accMedie}")
        durata = 1e-3*durata #schimbare din ms in s
        ultimaDist = 1/2 * accMedie*(durata)**2 # calculare distanta parcursa pe baza acceleratiei medie
        ultimaDurata = durata # stocare in variabile globale
        time.sleep(1e-3)
      time.sleep(1e-3) # se asteapta 1 ms

def citireAcc(accX, accY, accZ):
  global acX,acY,acZ,oldX,oldY,oldZ
  accAcum = accelerometru.acceleration
  oldX = accX
  oldY = accY
  oldZ = accZ
  acX = accAcum[0]
  acY = accAcum[1]
  acZ = accAcum[2]-9.8

while(True):
  citireAcc(acX,acY,acZ)
  print(acZ)
  verificareApasare(acX,acY,acZ)
  print(f"se apasa {apasare} \noldX:{oldX} oldY:{oldY} oldZ:{oldZ} \napasari {apasari}")
  if(apasare == False):
      print(f"ultima dist {ultimaDist} \nultima durata {ultimaDurata} \nacceleratie medie {accMedie} \napasari {apasari}")
