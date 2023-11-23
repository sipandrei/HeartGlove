#presupunem accelerometru ADXL345
#folosim libraria adafruit_adxl34x
#folosim picovoice pentru speech recognition https://www.picovoice.ai
import os
import time
import board
import busio
import adafruit_adxl34x
import pvrhino
import pvrecorder

# Variabile pentru input audio și Picovoice
devices = PvRecorder.get_available_devices()
recorder = PvRecorder(frame_length=512, device_index = 0)
recorder.start()
ACCES_KEY = os.environ.get("ACCESS_KEY", ".env")
CONTEXT_PATH = os.environ.get("CONTEXT_PATH", ".env")
rhino = pvrhino.create(access_key='${ACCESS_KEY}',context_path='${CONTEXT_PATH}')

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

# Variabile cu informații despre apăsări
distJos = 0.035 # apasare minima de 3 centimetri jumatate
distSus = 0.055 # apasare maxima de 5 centimetri jumatate
durJos = 95 # cadenta minima de 95 de apasari pe minut
durSus = 105 # cadenta maxima de 105 de apasari pe minut
marjaAcc = -2 # diferența minimă de accelerație de 2 m/s^2 pentru considerarea mișcării -
# este cu minus deoarece în timpul apasarii se merge spre -Z
ultimaDist = 0
ultimaDurata = 0
apasari = 0
apasare = False

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
  if abs(accx - oldX) < marjaAcc and abs(accY - oldY) < marjaAcc:
    if accZ - oldZ > marjaAcc: # Verificare miscare doar pe axa Z
      apasare = True
      durata = 0
      sumAcc = 0 # initializare variabile pentru calcularea acceleratiei medie pe apasare
    while apasare == True:
      durata += 1
      sumAcc += abs(oldZ) # actualizare variabile pentru medie
      citireAcc(accX, accY, accZ) # citim acceleratia noua
      if accZ - oldZ < -marjaAcc: # verificare final apasare sau incepere decomprimare
        apasari += 1
        apasare = False # iesire din modul de apasare si incrementare numar apasari
        accMedie = sumAcc / durata
        durata = 1e-3*durata #schimbarae din ms in s
        ultimaDist = 1/2 * (accMedie*durata)**2 # calculare distanta parcursa pe baza acceleratiei medie
        ultimaDurata = durata # stocare in variabile globale
      time.sleep(1e-3) # se asteapta 1 ms

# Functie citire acceleratii
def citireAcc(accX, accY, accZ):
  accAcum = accelerometru.acceleration - 9.8
  oldX = accX
  oldY = accY
  oldZ = accZ
  accX = accAcum[0]
  accY = accAcum[1]
  accZ = accAcum[2]

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
  while apasari < 30:
    citireAcc(nowX, nowY, nowZ)
    verificareApasare(nowX, nowY, nowZ) # verificam apasari pana ajung la 30
    match verificareMarje(ultimaDist, distJos, distSus): # interpretare ultima apasare in functie de distanta
      case -1:
        smartPrint("Apasa mai profund!")
      case 1:
        smartPrint("Apasa mai putin!")
      case 0:
        smartPrint("Apasare OK")

    match verificareMarje(ultimaDurata*60, durJos, durSus): # interpretare ultima apasare in functie de durata
      case -1:
        smartPrint("Apasa mai rapid!")
      case 1:
        smartPrint("Apasa mai încet!")
      case 0:
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
  match tipVictima:
    case "childVictim":
      distJos = 4.5
      distSus = 5.5
    case "babyVictim":
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
