

import tkinter as tk
from tkinter import HORIZONTAL
import RPi.GPIO as GPIO
import time
import spi

SPI_CLK = 23
#SPI_MISO = 21
SPI_MOSI = 19
SPI_CS = 24
Clock = 36 # BCM16
Address = 38 # BCM20
DataOut = 40 # BCM21


class Application:
    def __init__(self, master):
        self.master = master
      
        self.Exitbutton = tk.Button(master, text = "Exit", bg = "yellow", command = master.quit)
        self.Exitbutton.pack()

        self.w=tk.Scale(master, from_ = 0, to = 128, orient = HORIZONTAL)
        self.w.pack()

        self.w_adc=tk.Scale(master, from_ = 0, to = 1024, orient = HORIZONTAL)
        self.w_adc.pack()

        self.b=tk.Button(master, text = 'POT', command = self.shows).pack()

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        # Potentiometer MCP413x
        GPIO.setup(SPI_MOSI, GPIO.OUT)
        #GPIO.setup(SPI_MISO, GPIO.IN)
        GPIO.setup(SPI_CLK, GPIO.OUT, initial = GPIO.LOW)
        GPIO.setup(SPI_CS, GPIO.OUT, initial = GPIO.HIGH)
        # ADC TLC1543
        GPIO.setup(DataOut, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(Address, GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(Clock, GPIO.OUT, initial=GPIO.LOW) 

    def send_twobytes(self, bajt1, bajt2):
        LOW = GPIO.LOW
        HIGH = GPIO.HIGH
            
        GPIO.output(SPI_CLK, LOW) # Start with clock low
        GPIO.output(SPI_CS, LOW)  # Enable chip

        for i in range(8):
            if bajt1 & 0x80:  
                GPIO.output(SPI_MOSI, HIGH)
            else:
                GPIO.output(SPI_MOSI, LOW)
            time.sleep(0.0001)
            GPIO.output(SPI_CLK, HIGH) # Clock pulse high
            time.sleep(0.0001)
            GPIO.output(SPI_CLK, LOW) # Clock pulse low
            time.sleep(0.0001)
            bajt1 <<= 1  # Shift left,MSB first

        for i in range(8):
            if bajt2 & 0x80:  
                GPIO.output(SPI_MOSI, HIGH)
            else:
                GPIO.output(SPI_MOSI, LOW)
            time.sleep(0.0001)
            GPIO.output(SPI_CLK, HIGH) # Clock pulse high
            time.sleep(0.0001)
            GPIO.output(SPI_CLK, LOW) # Clock pulse low
            time.sleep(0.0001)
            bajt2 <<= 1  # Shift left,MSB first
            
        GPIO.output(SPI_CS,HIGH)
        time.sleep(0.001)


    def readADC(self, channel):
        MSBbajt = 0
        LSBbajt = 0
        if channel > 7 or channel < 0:  # illegal channel
            return -1

        GPIO.output(Clock, GPIO.LOW)  # Start with clock low
        channel <<= 4

        for i in range(4):
            if channel & 0x80:
                GPIO.output(Address, GPIO.HIGH)
            else:
                GPIO.output(Address, GPIO.LOW)

            GPIO.output(Clock, GPIO.HIGH)  # Clock pulse
            GPIO.output(Clock, GPIO.LOW)
            channel <<= 1

        for i in range(6):
            GPIO.output(Clock, GPIO.HIGH)  # Clock pulse
            GPIO.output(Clock, GPIO.LOW)
       
        time.sleep(0.0001)
       
          
        for i in range(2):
            GPIO.output(Clock, GPIO.HIGH)
            MSBbajt <<= 1
            if GPIO.input(DataOut):
                MSBbajt |= 0x01
            GPIO.output(Clock, GPIO.LOW)

            data = 0
        for i in range(8):
            GPIO.output(Clock, GPIO.HIGH)
            LSBbajt <<= 1
            if GPIO.input(DataOut):
                LSBbajt |= 0x01
            GPIO.output(Clock, GPIO.LOW)

        data = MSBbajt
        data <<= 8
        data |= LSBbajt
        return data



    def shows(self):
        self.setup()
        channel = 6
        print(self.w.get())
        a=self.w.get()
        self.send_twobytes(0x00, a)
        data = self.readADC(channel)
        print (data)
        self.w_adc.set(data)
        

root = tk.Tk()
app = Application(root)
root.mainloop()
