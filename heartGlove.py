
#presupunem accelerometru ADXL345
#folosim libraria adafruit_adxl34x
#folosim picovoice pentru speech recognition https://www.picovoice.ai
import busio
import os
import time
import board
import adafruit_adxl34x
import pvrhino
from pvrecorder import PvRecorder
import env
import math
import busio
from threading import Thread

#librarii afisare SSD1306 OLED
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import Adafruit_SSD1306

#initializare display
RST = None
display = Adafruit_SSD1306.SSD1306_128_64(rst = RST, i2c_bus = 4)
display.begin()
#variabile display
width = display.width
height = display.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)
padding = -2
top = padding
bottom = height-padding
x = padding
#variabile Font
sizeS = 9
sizeB = 14
fontBig = ImageFont.truetype('./fonts/fontMare.ttf', sizeB)
fontSmall = ImageFont.truetype('./fonts/fontMic.ttf', sizeS)
#curatare ecran
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
  i = Thread(target = display.display)
  i.start()
  i.join()

# Variabile pentru input audio și Picovoice
devices = PvRecorder.get_available_devices()
print(devices)
ACCESS_KEY = f"{env.access_key}"
CONTEXT_PATH = f"{env.context_path}"
print(f'{ACCESS_KEY}')
print(CONTEXT_PATH)

try:
	rhino = pvrhino.create(access_key=ACCESS_KEY,context_path=CONTEXT_PATH, sensitivity=0.5,endpoint_duration_sec=1.0, require_endpoint=True)
except pvrhino.RhinoInvalidArgumentError as e:
        print("One or more arguments provided to Rhino is invalid: ", args)
        print(e)
        raise e
except pvrhino.RhinoActivationError as e:
        print("AccessKey activation error")
        raise e
except pvrhino.RhinoActivationLimitError as e:
        print("AccessKey '%s' has reached it's temporary device limit" % args.access_key)
        raise e
except pvrhino.RhinoActivationRefusedError as e:
        print("AccessKey '%s' refused" % args.access_key)
        raise e
except pvrhino.RhinoActivationThrottledError as e:
        print("AccessKey '%s' has been throttled" % args.access_key)
        raise e
except pvrhino.RhinoError as e:
        print("Failed to initialize Rhino")
        raise e

recorder = PvRecorder(frame_length=rhino.frame_length, device_index = 2)
recorder.start()

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
distJos = 0.045 # apasare minima de 3 centimetri jumatate
distSus = 0.065 # apasare maxima de 5 centimetri jumatate
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

# Clasa cu functii legate de instructajul pentru masaj cardiac
class FunctiiProcedura:
  def constienta():
    smartPrint("se verifica starea de constienta a victimei")
  def caiAeriene():
    smartPrint("se verifica starea cailor aeriene")
  def verificareRespiratie():
    smartPrint("se verifica respiratia")
  def masaj():
    smartPrint("se fac 30 de apasari cu o cadenta de 100 pe minut si dupa 2 rasuflari, se repeta")

# Functii procesare audio

def get_next_audio_frame():
  return recorder.read()

# Functie principala picovoice
def sti():
  intent = ""
  audio_frame = get_next_audio_frame() # preluare audio
  is_finalized = rhino.process(audio_frame)
  if is_finalized:
    inference = rhino.get_inference()
    if inference.is_understood(): # verificare echivalenta input cu valorile definite
      intent = inference.intent
      slots = inference.slots
  return intent # transmitere numele valorii echivalente

def sti2():
  global recorder,rhino
  print("Waiting for input . . .")
  pcm = recorder.read()
  is_finalized = rhino.process(pcm)
  if is_finalized:
    inference = rhino.get_inference()
    if inference.is_understood:
      return inference.intent

# Algoritm verificare apasari
def verificareApasare(accX, accY, accZ):
  global sumaDurata,accMedie,oldX,oldY,oldZ,marjaAcc,apasare,apasari,ultimaDist,ultimaDurata
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
          if apasari%3==0:
            sumaDurata = 0
          sumaDurata += ultimaDurata

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
  return(mesaj)

# Functie ghidare respiratii
def rasuflari():
  displayInitialization()
  draw.text((x+20, top + sizeB*2), f'Give 2 Breaths', font = fontBig, fill = 255)
  displayImage()
  time.sleep(2)

def wrongCPR(apasareOk, vitezaOk):
  displayInitialization()
  draw.rectangle((0, 0, width, height), outline=0, fill=255)
  if apasareOk == False:
    draw.text((x+5, top + sizeB*1/2), "Wrong Amplitude", font = fontBig, fill=0)
  if vitezaOk == False:
    draw.text((x+5, top + sizeB*3/2), "Wrong Cadence", font = fontBig, fill=0)
  displayImage()
  #time.sleep(.2) de facut cu time.time

def pushFeedback(pushes, cadence, amplitude, apasareOk, vitezaOk):
  displayInitialization()
  draw.text((x+40, top + sizeB/2), f'{cadence} bpm {vitezaOk}', font = fontBig, fill = 255)
  draw.text((x+40, top + sizeB*3/2), f'{amplitude} cm {apasareOk}', font = fontBig, fill = 255)
  draw.text((x+40, top + sizeB*5/2), f'{pushes}/30', font = fontBig, fill = 255)
  displayImage()

"""   if pushes > 3 and (apasareOk == False or vitezaOk == False):
    wrongCPR(apasareOk, vitezaOk) """


# Functie interpretare apasari
def masterApasari():
  global cadenta,apasari
  apasari = 0
  timpStart = time.time()
  apasareOk = "ok"
  vitezaOk = "ok"
  while apasari < 30:
    citireAcc(nowX, nowY, nowZ)
    print(acZ)
    verificareApasare(nowX, nowY, nowZ) # verificam apasari pana ajung la 30
    marjeDist = verificareMarje(ultimaDist,distJos, distSus)
    # interpretare ultima apasare in functie de distanta
    if marjeDist == -1:
      apasareOk = "+"
      smartPrint("Apasa mai profund!")
    elif marjeDist == 1:
      apasareOk = "-"
      smartPrint("Apasa mai putin!")
    elif marjeDist == 0:
      smartPrint("Apasare OK")
      apasareOk = "="
    if math.floor(time.time()-timpStart) > 60:
      smartPrint("Timp prea mare pentru setul de apasari")
    """ if marjeDist != 0:
      apasareOk = False"""
    if apasari == 0 or sumaDurata == 0:
      if cadenta == 0:
        cadenta = 0
    else:
      cadenta = 60/(sumaDurata*10/(apasari%3+1))
    cadenta = round(cadenta,1)
    marjeDurata = verificareMarje(cadenta,durJos, durSus)
    # interpretare ultima apasare in functie de durata
    if marjeDurata == -1:
      vitezaOk = "+"
      smartPrint("Apasa mai rapid!")
    elif marjeDurata == 1:
      vitezaOk = "-"
      smartPrint("Apasa mai încet!")
    elif marjeDurata == 0:
      smartPrint("Apasare OK")
      vitezaOk = "="
    """if marjeDurata != 0:
      vitezaOk = False"""
    pushFeedback(apasari, cadenta, round(ultimaDist*100,1),apasareOk, vitezaOk)

# Functie tip victima in functie de input audio
def dateVictima():
  intent = sti2()
  if intent == "adult" or intent == "child" or intent == "babyVictim":
    return intent
  return ""

def instructions():
  global draw, top, sizeS, x, fontSmall, fontBig, distJos,distSus
  messages = ["CHECK victim", "CALL 112", "Place victim on \n flat surface", "GIVE 30 \nchest \ncompressions\nwhile kneeling ", 'Interlock hands \nPush on center \nof chest',"keep elbows\n LOCKED\npush from torso", "GIVE 2 breaths"]
  for number, message in enumerate(messages):
    displayInitialization()
    oneInstruction(number, message)
    displayImage()
    time.sleep(2)
  displayInitialization()
  draw.text((x, top + sizeB*0), '95 < cadence < 105', font = fontBig, fill=255)
  draw.text((x, top + sizeB*1), f'{round(distJos*100,1)} < depth < {round(distSus*100,1)}', font = fontBig, fill=255)
  displayImage()
  time.sleep(2)

# Functie prezentare procedura masaj cardiac
def prezentareProcedura():
  instructions()
  """ FunctiiProcedura.constienta()
  FunctiiProcedura.caiAeriene()
  FunctiiProcedura.verificareRespiratie()
  FunctiiProcedura.masaj() """

# Functie oprire pe baza input audio
def semnalStop():
  intent = sti2()
  print(f"intent: {intent}")
  if intent == "finish":
    return "finish"
  elif intent == "continue":
    return "continue"
  return ""

# Functie continuare pe baza input audio
def continuare():
  intent = sti2()
  if intent == "continue":
    return intent
  return ""

# Functie ajustare marje pe baza tipului de victima
def ajustareMarje(tipVictima):
  global distJos, distSus
  if tipVictima == "child":
    distJos = 0.035
    distSus = 0.045
  if tipVictima == "babyVictim":
    distJos = 0.033
    distSus = 0.043


# Functie initializare program, input date victima
def promptSetup(tipVictima):
  displayInitialization()
  draw.text((x+10, top + sizeB*1), "Child or Adult\nvictim", font = fontBig, fill=255)
  draw.text((x+10, top + sizeB*3), f'Current: {tipVictima}', font = fontBig, fill=255)
  displayImage()

def initialSetup():
  victima = ""
  promptSetup(victima)
  while victima == "":
    victima = dateVictima()
    smartPrint(f"Victim Data:{victima}")
    if victima != "":
      promptSetup(victima)
      time.sleep(0.5)
    ajustareMarje(victima) # modifica marje in functie de victima https://www.cpracademylv.com/infant-cpr-certification/

def continuePrompt():
  intent = ""
  displayInitialization()
  oneInstruction("","Waiting for start\ncommand")
  displayImage()
  while intent != "continue":
    intent = continuare()
  for i in range(3):
    displayInitialization()
    oneInstruction("",f'Starting in {3-i}')
    displayImage()
    time.sleep(1)

def verificareStop():
  intent = ""
  displayInitialization()
  oneInstruction("", "Stop or continue?")
  displayImage()
  while intent == "":
   intent = semnalStop()
  return intent


# Apelare functii
initialSetup()
prezentareProcedura()
stop = ""
while stop != "finish":
  continuePrompt()
  masterApasari()
  rasuflari()
  startInterval = time.time()
  stop = verificareStop()
  print(stop)
  time.sleep(2)
rhino.delete() # Oprire picovoice rhino
