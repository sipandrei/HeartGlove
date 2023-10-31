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

devices = PvRecorder.get_available_devices()

recorder = PvRecorder(frame_length=512, device_index = 0)
recorder.start()
ACCES_KEY = os.environ.get("ACCESS_KEY", ".env")
CONTEXT_PATH = os.environ.get("CONTEXT_PATH", ".env")
rhino = pvrhino.create(access_key='${ACCESS_KEY}',context_path='${CONTEXT_PATH}')

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

def get_next_audio_frame():
  return recorder.read()

def sti():
  audio_frame = get_next_audio_frame()
  is_finalized = rhino.process(audio_frame)
  if is_finalized:
    inference = rhino.get_inference()
    if inference.is_understood():
      intent = inference.intent
      slots = inference.slots
  return intent

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
    # de modificat marje in functie de adult,copil, bebelus https://www.cpracademylv.com/infant-cpr-certification/
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
  while not intent:
    intent = sti()
  if intent == "adultVictim" or intent == "childVictim" or intent == "babyVictim":
    return intent
  return 0

def prezentareProcedura():
  print("to implement screen")

def semnalStop():
  return False

def ajustareMarje(tipVictima):
  match tipVictima:
    case "childVictim":
      distJos = 4.5
      distSus = 5.5
      break
    case "babyVictim":
      distJos = 3.3
      distSus = 4.3
      break

victima = dateVictima()
ajustareMarje(victima)
prezentareProcedura()
while not semnalStop():
  masterApasari()
  rasuflari()
rhino.delete()
