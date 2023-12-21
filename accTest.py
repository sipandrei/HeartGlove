
import board
import busio
import adafruit_adxl34x

i2c = busio.I2C(board.SCL, board.SDA)
acc = adafruit_adxl34x.ADXL345(i2c)

while 1:
	print(acc.acceleration[2]-9.8)

