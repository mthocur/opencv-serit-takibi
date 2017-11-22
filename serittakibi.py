from imutils.video import VideoStream #webcam ve picamerayi ayni sinifta kullanabilimek icin gerekli class
import datetime
import argparse #parametre kullanimi icin gerekli kutuphane
import imutils
import time
import cv2 #opencv
import numpy as np
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT) #on motor a
GPIO.setup(11,GPIO.OUT) #on motor b
GPIO.setup(13,GPIO.OUT) #arka motor a
GPIO.setup(15,GPIO.OUT) #arka motor b
p=GPIO.PWM(13,100)  
p.start(1)
p.ChangeDutyCycle(80)   

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="Parametresiz webcam, --picamera parametresi ile picamera kullanimi")
args = vars(ap.parse_args())

# Video yayininin baslamasi icin gerekli ayarlar ve camera sensorleri icin 2 saniyelik bekleme suresi
vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(2.0)
kernel = np.ones((5,5), np.uint8)
width = 400
height = 300
baslangic = 60
bitis = 80
sayac2 = 0
ortanokta = int((bitis-baslangic)/2) + baslangic;
fark = bitis-baslangic
renkesigi = 130
kameraorta = int(width / 2)

GPIO.output(7, False) #true
GPIO.output(11, False)
GPIO.output(13, False)
GPIO.output(15, False)

# Video yayini frame dongusu
while True:
	# yayindan frame aliniyor
	frame = vs.read()
	# alinan frame boyutlandiriliyor
	frame = imutils.resize(frame, width=400)
	
	original = frame #ekrana grayscale olmayan goruntunun basilmasi icin orjinal goruntu saklaniyor
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	frame = cv2.GaussianBlur(frame, (3, 3), 0)
	#goruntu uzerine asindirma yapiliyor
	frame = cv2.erode(frame, kernel, iterations=1)
	frame = cv2.dilate(frame, kernel, iterations=1)
	#threshold islemi yapiliyor
	ret, frame = cv2.threshold(frame,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
	#gereksiz islem yukundan kurtulmak icin kırpma yapiliyor
	frame = frame[baslangic:bitis, 0:width] 
	renkkontrol = False # siyah aranacak
	sayac = 0
	sayac2 = 0
	dizi = [0] * 20
	dizi2 = [0] * 20
	cv2.line(original,(150, ortanokta),(250,ortanokta),(100,255,100),5)
	for j in range(20,400):
	    if(renkkontrol):
	        if( frame[0:1, j:j+1] > renkesigi ):
	            renkkontrol = False
	            dizi[sayac] = j
	            sayac = sayac + 1
	            cv2.circle(original,(j,baslangic + 5), 5, (100,255,100), -1)
	    else:
	        if( frame[0:1, j:j+1] < renkesigi ):
	            renkkontrol = True
	            dizi[sayac] = j
	            sayac = sayac + 1
	            cv2.circle(original,(j,baslangic + 5), 5, (100,255,100), -1)
	for j in range(20,400):
	    if(renkkontrol):
	        if( frame[fark-1:fark, j-1:j] > renkesigi ):
	            renkkontrol = False
	            dizi2[sayac2] = j
	            sayac2 = sayac2 + 1
	            cv2.circle(original,(j,bitis - 5), 5, (100,255,100), -1)
	    else:
	        if( frame[fark-1:fark, j-1:j] < renkesigi ):
	            renkkontrol = True
	            dizi2[sayac2] = j
	            sayac2 = sayac2 + 1
	            cv2.circle(original,(j,bitis - 5), 5, (100,255,100), -1)
	dizi3=[None] * 20
	for a in range(0,4):
		cv2.line(original,(dizi[a], baslangic),(dizi2[a],bitis),(100,255,100),5)
		c = int((dizi[a] + dizi2[a]) / 2)
		dizi3[a] = c
		cv2.circle(original,(c,ortanokta), 5, (100,255,100), -1)
	sagorta = int((dizi3[0] + dizi3[1]) / 2)
	solorta = int((dizi3[2] + dizi3[3]) / 2)
	
	yolorta = int((sagorta + solorta) / 2)
	cv2.circle(original,(yolorta,ortanokta), 10, (255,0,0), -1)
	pozisyon = kameraorta-yolorta
	if( pozisyon > 20 ):
		#yoldan sag tarafa uzaklasilmis sol ileri gidilecek
		GPIO.output(7, True) #true
		GPIO.output(11, False)
		GPIO.output(13, True)
		GPIO.output(15, False)
	elif( pozisyon < -20 ):
		#yoldan sol tarafa uzaklasilmis sag ileri gidilecek
		GPIO.output(7, False)
		GPIO.output(11, True) #treu
		GPIO.output(13, True)
		GPIO.output(15, False)
	else:
		GPIO.output(7, False)
		GPIO.output(11, False) #treu
		GPIO.output(13, False)
		GPIO.output(15, False)
	# frame ekrana basiliyor
	cv2.imshow("Frame", original)
	key = cv2.waitKey(1) & 0xFF
	# q tusuna basilirsa uygulama sonlaniyor
	if key == ord("q"):
		break

# islemlerin ve pencerelerin sonlandirilmasi
cv2.destroyAllWindows()
vs.stop()
