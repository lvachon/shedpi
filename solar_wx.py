import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_bme280
import requests
import neopixel
import digitalio
import pwmio

pixel_pin = board.D18
fan_pin = board.D23
tumbler_pin = board.D25
ORDER = neopixel.GRB
num_pixels = 8
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)
fan = digitalio.DigitalInOut(fan_pin)
fan.direction = digitalio.Direction.OUTPUT
tumbler = pwmio.PWMOut(tumbler_pin,frequency=1000,duty_cycle=0)
#tumbler.direction = digitalio.Direction.OUTPUT
#tumbler.value = False
oncycle = 49000
# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c,0x76)
# Create single-ended input on channel 0
solar = AnalogIn(ads, ADS.P0)
batt = AnalogIn(ads, ADS.P1)

while True:
	try:
		solarV = solar.voltage*11
		battV = batt.voltage*11
		temp = bme280.temperature*9/5+32
		pres = bme280.pressure*0.02953
		humid = bme280.humidity
		url = "http://lucvachon.com/solar.php?solar={:>5.4f}&batt={:>5.4f}&temp={:>5.4f}&pres={:>5.6f}&humid={:>5.4f}".format(
	    		solarV,
	    		battV,
	    		temp,
	    		pres,
	    		humid)
		r = requests.get(url)
		print(url)
		for i in range(0,num_pixels):
			r=0
			g=0
			b=0
			if(solarV>12+i):
				b=min(255,(int)(255*(solarV-12-i)))
			if(battV>12+i*0.25):
				g=min(255,(int)(1023*(battV-12-i*0.25)))
			if(temp>10+i*10):
				r=min(255,(int)(25.5*(temp-10-i*10)))
			if(solarV<12):
				r*=max(0.075,solarV/14)
				g*=max(0.075,solarV/14)
				b*=max(0.075,solarV/14)
			pixels[num_pixels-1-i]=((int)(r),(int)(g),(int)(b))
		pixels.show()
		if(temp>95 and battV>13.1):
			fan.value = True
		if(temp<90 or battV<13):
			fan.value = False
		if(temp>50 and battV>13.1):
			tumbler.duty_cycle = oncycle
		if(temp<35 or battV<13):
			tumbler.duty_cycle = 0
	except Exception as err:
		print("Poo {0}".format(err))
	time.sleep(10)

