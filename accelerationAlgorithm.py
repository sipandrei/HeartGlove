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
  if abs(accX) < marjaAcc+8 and abs(accY) < marjaAcc+8:
    if accZ > marjaAcc: # Verificare miscare doar pe axa Z
      apasare = True
      inflex = 0
      durata = time.time()
      instDur = durata
      vel = 0
      sumAcc = 0 # initializare variabile pentru calcularea acceleratiei medie pe apasare
      while inflex < 2:
        vel += oldZ*(time.time()-instDur) # actualizare variabile pentru medie
        instDur = time.time()
        oldZ = accZ
        accZ = accelerometru.acceleration[2]-9.8 # citim acceleratia noua
        if abs(accZ) < 0.5:
          accZ = 0
        print(accZ)
        if accZ < -1:
          inflex = inflex + 1
        if inflex == 2 : # verificare final apasare sau incepere decomprimare
          print(f"suma acc {sumAcc}")
          apasari += 1
          apasare = False # iesire din modul de apasare si incrementare numar apasari
          durata = time.time() - durata #schimbare din ms in s
          accMedie = vel/durata #m/ms^2
          print(f"ultima acc {accMedie}")
          ultimaDist = vel*(durata)/2 # calculare distanta parcursa pe baza acceleratiei medie
          ultimaDurata = durata/2 # stocare in variabile globale

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
