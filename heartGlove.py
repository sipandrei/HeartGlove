
#presupunem accelerometru ADXL345
#folosim libraria adafruit_adxl34x
#folosim picovoice pentru speech recognition https://www.picovoice.ai
import os
import time
import board
import adafruit_adxl34x
import pvrhino
from pvrecorder import PvRecorder
import env
import math

# Variabile pentru input audio și Picovoice
devices = PvRecorder.get_available_devices()
recorder = PvRecorder(frame_length=512, device_index = 0)
recorder.start()
ACCESS_KEY = f"{env.access_key}"
CONTEXT_PATH = f"{env.context_path}"
print(f'{ACCESS_KEY}')
print(CONTEXT_PATH)

try:
	rhino = pvrhino.create(
        access_key=ACCESS_KEY,
        context_path=CONTEXT_PATH)
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
accMedie = 0

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
  audio_frame = get_next_audio_frame() # preluare audio
  is_finalized = rhino.process(audio_frame)
  if is_finalized:
    inference = rhino.get_inference()
    if inference.is_understood(): # verificare echivalenta input cu valorile definite
      intent = inference.intent
      slots = inference.slots
  return intent # transmitere numele valorii echivalente

# Algoritm verificare apasari
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

# Functie ghidare respiratii
def rasuflari():
  smartPrint("2 respiratii")
  time.sleep(3)

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

# Functie tip victima in functie de input audio
def dateVictima():
  intent = sti()
  if intent == "adultVictim" or intent == "childVictim" or intent == "babyVictim":
    return intent
  return ""

# Functie prezentare procedura masaj cardiac
def prezentareProcedura():
  print("to implement screen")
  FunctiiProcedura.constienta()
  FunctiiProcedura.caiAeriene()
  FunctiiProcedura.verificareRespiratie()
  FunctiiProcedura.masaj()

# Functie oprire pe baza input audio
def semnalStop():
  intent = sti()
  if intent == "finish":
    return True
  return False

# Functie continuare pe baza input audio
def continuare():
  intent = sti()
  if intent == "stepDone":
    return True
  return False

# Functie ajustare marje pe baza tipului de victima
def ajustareMarje(tipVictima):
  if tipVictima == "childVictim":
    distJos = 4.5
    distSus = 5.5
  if tipVictima == "babyVictim":
    distJos = 3.3
    distSus = 4.3


# Functie initializare program, input date victima
def initialSetup():
  victima = ""
  while victima == "":
    smartPrint("Victim Data")
    victima = dateVictima()
    ajustareMarje(victima) # modifica marje in functie de victima https://www.cpracademylv.com/infant-cpr-certification/

# Apelare functii
initialSetup()
prezentareProcedura()
while not semnalStop():
  masterApasari()
  rasuflari()
rhino.delete() # Oprire picovoice rhino
