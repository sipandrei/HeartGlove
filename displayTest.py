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

sizeS = 7
sizeB = 11
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

def instructions():
  global draw, top, sizeS, x, fontSmall, fontBig
  messages = ["CHECK victim", "CALL 112", "Place victim on \n flat surface", "GIVE 30 \nchest compressions\nwhile kneeling ", 'Interlock hands \nPush on center \nof chest',"keep elbows LOCKED\npush from torso", "GIVE 2 breaths"]
  for number, message in enumerate(messages):
    oneInstruction(number, message)
    displayImage()
    time.sleep(2)
    displayInitialization()
  draw.text((x, top + sizeB*0), '95 < cadence < 105', font = fontBig, fill=255)
  draw.text((x, top + sizeB*1), 'Rate depending \non victim', font = fontBig, fill=255)
  displayImage()

instructions()
