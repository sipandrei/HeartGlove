
import time
import board
import busio
import adafruit_adxl34x
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import Adafruit_SSD1306
from threading import Thread

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
sumaDurata = 0
cadenta = 0

def verificareApasare(accX, accY, accZ):
  global accMedie,oldX,oldY,oldZ,marjaAcc,apasare,apasari,ultimaDist,ultimaDurata, sumaDurata
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
          ultimaDurata = durata # stocare in variabile globale
          if apasari%3==0:
            sumaDurata = 0
          sumaDurata += ultimaDurata 

def citireAcc(accX, accY, accZ):
  global acX,acY,acZ,oldX,oldY,oldZ
  accAcum = accelerometru.acceleration
  oldX = accX
  oldY = accY
  oldZ = accZ
  acX = accAcum[0]
  acY = accAcum[1]
  acZ = accAcum[2]-9.8
#  time.sleep(0.1)

RST = None

display = Adafruit_SSD1306.SSD1306_128_64(rst = RST, i2c_bus=4)
display.begin()

width = display.width
height = display.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)
padding = -2
top = padding
bottom = height - padding
x = padding

sizeS = 9
sizeB = 17
fontBig = ImageFont.truetype('./fonts/fontMare.ttf', sizeB)
fontSmall = ImageFont.truetype('./fonts/fontMic.ttf', sizeS)

display.clear()
display.display()

def displayInitialization():
  global draw
  draw.rectangle((0,0,width,height), outline=0, fill=0)

def oneInstruction(number, message):
  global draw, top, sizeS, x, fontSmall, fontBig
  draw.text((x, top + 0), f'{number}.', font = fontSmall, fill=255)
  draw.text((x+3, top + sizeS), f'{message}', font = fontBig, fill = 255)

def displayImage():
  global image,display
  display.image(image)
  x=Thread(target = display.display)
  x.start()
  x.join()

def wrongCPR(apasareOk, vitezaOk):
  displayInitialization()
  draw.rectangle((0, 0, width, height), outline=0, fill=255)
  if apasareOk == False:
    draw.text((x+5, top + sizeB*1/2), "Wrong Cadence", font = fontBig, fill=0)
  if vitezaOk == False:
    draw.text((x+5, top + sizeB*3/2), "Wrong Speed", font = fontBig, fill=0)
  displayImage()


def pushFeedback(pushes, cadence, amplitude, apasareOk, vitezaOk):
  displayInitialization()
  draw.text((x+30, top + sizeB/2), f'{cadence} bpm', font = fontBig, fill = 255)
  draw.text((x+30, top + sizeB*3/2), f'{amplitude} cm', font = fontBig, fill = 255)
  draw.text((x+30, top + sizeB*5/2), f'{pushes}/30', font = fontBig, fill = 255)
  displayImage()

  if apasareOk == False or vitezaOk == False:
    wrongCPR(apasareOk, vitezaOk)

while(True):
  citireAcc(acX,acY,acZ)
  print(acZ)
  verificareApasare(acX,acY,acZ)
  print(f"se apasa {apasare} \noldX:{oldX} oldY:{oldY} oldZ:{oldZ} \napasari {apasari}")
  if(apasare == False):
      print(f"ultima dist {ultimaDist} \nultima durata {ultimaDurata} \nacceleratie medie {accMedie} \napasari {apasari}")
  if apasari==0 or sumaDurata==0:
    if cadenta == 0:
      cadenta = 0
  else:
    cadenta = 60/(sumaDurata*10/(apasari%3+1))
  pushFeedback(apasari, round(cadenta, 1), round(ultimaDist*100,1),True, True)

