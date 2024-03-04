from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import Adafruit_SSD1306
import time

RST = None

display = Adafruit_SSD1306.SSD1306_128_32(rst = RST, i2c_bus=1)
width = display.width
height = display.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)
padding = -2
top = padding
bottom = height - padding
x = 0

sizeS = 9
sizeB = 14
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
  display.display()

def smartPrint(mesaj):
  print(mesaj)
  return(mesaj)

def instructions():
  global draw, top, sizeS, x, fontSmall, fontBig
  messages = ["CHECK victim", "CALL 112", "Place victim on flat surface", "GIVE 30 chest compressions", "GIVE 2 breaths"]
  for number, message in enumerate(messages):
    oneInstruction(number, message)
    displayImage()
    time.sleep(1)
    displayInitialization()
  draw.text((x, top + 0), "for COMPRESSIONS", font = fontSmall, fill=255)
  draw.text((x, top + sizeS), "place hands centered on chest", font = fontSmall, fill=255)
  draw.text((x, top + sizeS*2), "elbows locked, stand over hands", font = fontSmall, fill=255)
  draw.text((x, top + sizeS*3), "95 < cadence < 105", font = fontSmall, fill=255)
  draw.text((x, top + sizeS*3), "Rate depending on victim", font = fontSmall, fill=255)
  displayImage()

def wrongCPR(apasareOk, vitezaOk):
  displayInitialization()
  draw.rectangle((0, 0, width, height), outline=0, fill=255)
  if apasareOk == False:
    draw.text((x, top + sizeS), "Wrong Cadence", font = fontBig, fill=0)
  if vitezaOk == False:
    draw.text((x, top + sizeS*2), "Wrong Speed", font = fontBig, fill=0)
  time.sleep(.5)

def pushFeedback(pushes, cadence, amplitude, apasareOk, vitezaOk):
  displayInitialization()
  draw.text((x+3, top + sizeB), f'{cadence} bpm', font = fontBig, fill = 255)
  draw.text((x+3, top + sizeB*2), f'{amplitude} cm', font = fontBig, fill = 255)
  draw.text((x+3, top + sizeB*3), f'{pushes}/30', font = fontBig, fill = 255)
  time.sleep(.5)
  if apasareOk == False or vitezaOk == False:
    wrongCPR(apasareOk, vitezaOk)

def breathInfo():
  displayInitialization()
  draw.text((x+3, top + sizeB*2), f'Give 2 Breaths', font = fontBig, fill = 255)
  time.sleep(3)

instructions()
