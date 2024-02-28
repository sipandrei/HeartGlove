import board
import busio
import adafruit_ssd1306
import time

i2c = busio.I2C(board.SCL,board.SDA)

disp = adafruit_ssd1306.SSD1306(128, 32, i2c)
width = display.width
height = display.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)
padding = -2
top = padding
bottom = height - padding
x = 0
sizeS = 9
sizeB = 12
fontBig = ImageFont.truetype('./fonts/fontMare.ttf', sizeB)
fontSmall = ImageFont.truetype('./fonts/fontMic.ttf', sizeS)

def displayInitialization():
  global disp
  disp.fill(0)
  disp.show()

def oneInstruction(number, message):
  global draw, top, sizeS, x, fontSmall, fontBig
  draw.text((x, top + 0), f'{number}.', font = fontSmall, fill=255)
  draw.text((x+3, top + sizeS), f'{message}', font = fontBig, fill = 255)

def instructions():
  global draw, top, sizeS, x, fontSmall, fontBig
  messages = ["CHECK victim", "CALL 112", "Place victim on flat surface", "GIVE 30 chest compressions", "GIVE 2 breaths"]
  for number, message in enumerate(messages):
    oneInstruction(number, message)
    time.sleep(1)
    displayInitialization()
  draw.text((x, top + 0), "for COMPRESSIONS", font = fontSmall, fill=255)
  draw.text((x, top + sizeS), "place hands centered on chest", font = fontSmall, fill=255)
  draw.text((x, top + sizeS*2), "elbows locked, stand over hands", font = fontSmall, fill=255)
  draw.text((x, top + sizeS*3), "95 < cadence < 105", font = fontSmall, fill=255)
  draw.text((x, top + sizeS*3), "Rate depending on victim", font = fontSmall, fill=255)

width = disp.fill
height = disp.height
