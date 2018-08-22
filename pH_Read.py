
import serial
import time
import re
import ast
from array import array


#time.sleep(0.25)
#open pH meter com channel
comph=7  #raw_input("pH METER SETUP: enter com port for pH meter [5]: " or int(4))
compah=(comph-1)
elementph=8 #raw_input("pH METER SETUP:enter tuple element for pH or mV [default: 8 for pH] [12 for mV]:   ") or 8
serph=serial.Serial(port=compah,baudrate=38400,timeout=0.1)
junka = serph.write('getmeas\r')# clears pH meter buffer
serph.write('set ReadMode 0\r')
time.sleep(1)
phval=0
a=serph.write('getmeas\r')
time.sleep(1.00)
b = serph.read(1000)
meter_list = b.split(",")
serialNum = meter_list[1]
                
while True:
        #time.sleep(1.25)
        a=serph.write('getmeas\r')
        time.sleep(0.5) #Recommend sleep minimum of 0.5, though code will run properly for smaller values
        b=serph.read(1000)
        meter_list=b.split(",")
        #print meter_list

        try:
            testNum = meter_list[1]
            if testNum == serialNum:
                t = meter_list[4]
                phval=meter_list[8]
                print '\n pH = %s'%phval+', time = %s'%t
            else:
                continue
        except:
            continue


            #serph.close()


