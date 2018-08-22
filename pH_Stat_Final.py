
import serial
import time
import re
import ast
from array import array
import sys


#Proportional-Integration-Derivative
#Needs to include timing control, specifying the units of pumping rate (which depend on the syringe you use)
#Last updated: March 14th, 2016

class PID:
    """
    Discrete PID control
    """

    def __init__(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500):

        self.Kp=P
        self.Ki=I
        self.Kd=D
        self.Derivator=Derivator #A holder for the t(i-1) value
        self.Integrator=Integrator #A holder for the approximate integral value for the integrator (which should be adjusted based on the time between steps)
        self.Integrator_max=Integrator_max
        self.Integrator_min=Integrator_min

        self.set_point=0.0
        self.error=0.0

    def update(self,current_value):
        """
        Calculate PID output value for given reference input and feedback
        """

        self.error = self.set_point - current_value

        self.P_value = self.Kp * self.error
        self.D_value = self.Kd * ( self.error - self.Derivator) #Need to divide by time
        self.Derivator = self.error

        self.Integrator = self.Integrator + self.error

        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min

        self.I_value = self.Integrator * self.Ki

        PID = self.P_value + self.I_value + self.D_value

        return PID

    def setPoint(self,set_point):
        """
        Initilize the setpoint of PID
        """
        self.set_point = set_point
        self.Integrator=0
        self.Derivator=0

    def setIntegrator(self, Integrator):
        self.Integrator = Integrator

    def setDerivator(self, Derivator):
        self.Derivator = Derivator

    def setKp(self,P):
        self.Kp=P

    def setKi(self,I):
        self.Ki=I

    def setKd(self,D):
        self.Kd=D

    def getPoint(self):
        return self.set_point

    def getError(self):
        return self.error

    def getIntegrator(self):
        return self.Integrator

    def getDerivator(self):
        return self.Derivator


class init:

        answer="no"
        try:
            while answer == "no":
     
                #open pH meter com channel
                comph=4 #raw_input("pH METER SETUP: enter com port for pH meter [5]: " or int(7))
                compah=(comph-1)
                timeoutph=0.01#raw_input("pH METER SETUP:enter timeout value for COM port communication [0.001 sec]:   ") or 0.001
                elementph=8 #raw_input("pH METER SETUP:enter tuple element for pH or mV [default: 8 for pH] [12 for mV]:   ") or 8
                serph=serial.Serial(port=compah,baudrate=9600,timeout=timeoutph)
                junka = serph.write('getmeas\r')# return initial values
    
    
                #open syringe pump com channel
                comsyringe=3 #raw_input("SYRINGE PUMP SETUP: enter com port for NE-1000 syringe pump [4]:  ") or int(4)
                comsyringeh=int(comsyringe-1)
                syringetimeout=0.01#raw_input("SYRINGE PUMP SETUP: enter timeout value for COM port communication [0.001 sec]:   ") or 0.001                         
                diam=raw_input("SYRINGE PUMP SETUP: enter Syringe Diameter (max 26.7 mm):  ") or 26.7
                sersyringe=serial.Serial(port=comsyringeh,baudrate=19200,timeout=syringetimeout)
                #sersyringe.write("*RESET \r")
                sersyringe.write("DIA %s \r" % diam)
                time.sleep(0.05)
                sersyringe.write("CLD INF \r \r") # clears infusing volume counter
                time.sleep(0.05)
                trackvol=0 #initial volume infused
    
    
                #get initial pH measurement             
                a=serph.write('getmeas\r')
                time.sleep(0.05)
                b=serph.read(1000)
                meter_list=b.split(",")
                phval=meter_list[8]
                phvalint="%0.2f"%int(float(phval))
                serialNum = meter_list[1]
                t = meter_list[4]
    
                #setpoints
                setpointi=raw_input("\r\r\r\r enter pH setpoint:   ") or 7.0
                updown=raw_input("titrating from low to high pH [base] or high to low pH [acid, any key]:   ") or "base"
    
                print "\r\r\r\r initial pH value: " + repr(phvalint)
                #answer = raw_input("\r type [no] if pH value is incorrect or you would like to re-enter parameters. any other key to continue:   ") or "no"
                #if answer == "no":
                #        serph.close()
                #        sersyringe.close()
    
                p=raw_input("enter values for P,I,D (return after each entry)[2.0]: ") or 2.0
                i=raw_input("\r \r \r [1.0]:   ") or 1.0
                d=raw_input("\r \r [1.0]:  ") or 1.0
                #scaleing = int(raw_input("enter scaling factor for pid to pump [50]" or 50.0))
                
    
                filename = raw_input("enter file name with .txt extension:") or "phstat.txt"
                text_file = open(filename,"w")
                text_file.close()
            
    
                max_vol=float(raw_input("enter maximum titrant volume [2000 mL]:") or 2000.0)
                syringevolumemax = int(raw_input("enter maximum integer value of syringe volume to be dispensed [1]") or 1)
                junkola = raw_input("press return to start")
                cycles = 0
    
              
    
    
                #PID algorithm vs. titration down
            
                if updown == "base":
                        
                    countvol=0
                    p=PID(p,i,d)
                    p.setPoint(float(setpointi))
                    sersyringe.write("DIR INF\r")
                    time.sleep(0.1)
                    ph_setpoint=float(setpointi)
                    ph_value=float(phval)
                    print "pH value: " + repr(ph_value)
                    print "pH setpoint: " + repr(ph_setpoint)
                    phvalint=int(ph_value)
    
                    
                    
        
                    while max_vol > countvol:
    
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
    
                          
                           
                           try:
                                   ph_setpoint=float(setpointi)
                           except:
                                 continue
    
                           try:
                                   ph_value=float(phval)
                           except:
                                 continue
                            
                           
                           print "Setpoint: " + repr(setpointi)
                           print "pH value: " + phval
                          
                           pid = p.update(ph_value)*100
                           abspid = (abs(pid))
    
     
                           while ph_value >= ph_setpoint:
                                   
                                   print "setpoint reached!!!  "
                                   print "Setpoint: " + repr(setpointi)
                                   print "pH value: " + phval
                                   sersyringe.write("RAT 0 \r")
                                   time.sleep(0.25)
                                   ts=time.time()
                                   xx=countvol
                                   #outputs = str([ph_setpoint,ph_value,float(xx),ts,"\n"])
                                   #text_file = open(filename,"a")
                                   #text_file.write(outputs) # write outputs and timestamp to file
                                   #text_file.close()
    
    
                                   a=serph.write('getmeas\r')
                                   time.sleep(0.5) #Recommend sleep minimum of 0.5, though code will run properly for smaller values
                                   b=serph.read(1000)
                                   time.sleep(0.1)
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
    
                                   try:
                                           
                                           ph_value=float(meter_list[8])
    
                                   except:
                                           continue
                                    
                                   time.sleep(0.1)
    
    
                                   
                           print "PID value:" + repr(abspid)
                           print "adding base!"
                           sersyringe.write("DIR INF\r")
                           time.sleep(0.15)
                           sersyringe.write("RAT%s\r" % abspid) #Set rate... but what are the units? guessing mL/min
                           time.sleep(0.15)
                           sersyringe.write("RUN\r")
                           time.sleep(0.15)
                           sersyringe.write("DIS\r")
                           time.sleep(0.15)
                           #sersyringe.write("DIS\r")
                           #time.sleep(0.1)
                           ivolume=sersyringe.read(100)
                           time.sleep(0.15)
                           infusedvolume=ivolume.split("")
                           splitinfuse = infusedvolume[3]
                           splitvals = splitinfuse.split("W")
                           infused = splitvals[0]
                           infusedfloat=re.findall('\d+.\d+',infused)                       
                           #print type(infusedfloat)
                           qqq=''.join(infusedfloat)
                           z=len(qqq)
                           xx=qqq[0:z]
                           #print xx
                           
                           #outputs = str([ph_setpoint,ph_value,infusedfloat,t,"\n"])
                           
                           #text_file = open(filename,"a")
                           #text_file.write(outputs) # write outputs and timestamp to file
                           #text_file.close()
    
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
                                 #print '\n pH = %s'%phval+', time = %s'%t
                             else:
                                 continue
                           except:
                                 continue
                           ph_value=phval
    
                           
    
                           
                           if z>0:
                                   voltrack = int(float(xx))
                                   print "Volume infused: " + repr(xx)
                                   diffvoltrack= voltrack-trackvol
                                   if diffvoltrack>= syringevolumemax:
                                           cycles = cycles +1
                                           print "Re-filling syringe!"
                                           print "cycle: %s" % cycles
                                           
                                           sersyringe.write("STP \r")
                                           print "pump stopped"
                                           time.sleep(0.1)
                                           
                                           sersyringe.write("VOL 0 \r")
                                           print "volume set to continous pump"
                                           time.sleep(0.1)
                                           
                                           sersyringe.write("RAT 800.0\r")
                                           print "rate set"
                                           time.sleep(0.1)
                                           
                                           sersyringe.write("DIR REV \r") 
                                           print "direction reversed"
                                           time.sleep(0.1)
                                           
                                           sersyringe.write("VOL %s \r" % syringevolumemax)
                                           print ("volume set to %s" % syringevolumemax)
                                           time.sleep(0.1)
    
                                           sersyringe.write("RUN \r")
                                           print "syringe re-fill..titration will resume shortly..."
    
                                           time.sleep(syringevolumemax*5)
                                           sersyringe.write("VOL 0 \r\r")
                                           print "reset pumping to continous"
                                           time.sleep(0.1)
                                           sersyringe.write("DIR REV\r\r")
                                           print "reverse direction and exit loop..."
                                           time.sleep(0.1)                                       
                                           trackvol=trackvol+syringevolumemax
                                   
                           else: print("no value returned from pump")
    
                           
                else:
                        
                    countvol=0
                    p=PID(int(p),int(i),int(d))
                    p.setPoint(float(setpointi))
                    sersyringe.write("DIR INF\r")
                    time.sleep(0.1)
                    ph_setpoint=float(setpointi)
                    ph_value=float(phval)
                    print "pH value: " + repr(ph_value)
                    print "pH setpoint: " + repr(ph_setpoint)
                    phvalint=int(ph_value)
    
                    
                    
        
                    while max_vol > countvol:
    
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
    
                           ph_setpoint=float(setpointi)
                           ph_value=float(phval)
                           print "Setpoint: " + repr(setpointi)
                           print "pH value: " + phval
                          
                           pid = p.update(ph_value)*100
                           abspid = (abs(pid))
                           
                           while ph_value <= ph_setpoint:
                                   
                                   print "setpoint reached!!!  "
                                   print "Setpoint: " + repr(setpointi)
                                   print "pH value: " + phval
                                   sersyringe.write("RAT 0 \r")
                                   time.sleep(0.15)
                                   ts=time.time()
                                   xx=countvol
                                   #outputs = str([ph_setpoint,ph_value,float(xx),ts,"\n"])
                                   #text_file = open(filename,"a")
                                   #text_file.write(outputs) # write outputs and timestamp to file
                                   #text_file.close()
    
    
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
                                   try:
                                           
                                           ph_value=float(meter_list[8])
                                   except:
                                           continue
                                   time.sleep(0.1)
                                   
                           print "PID value:" + repr(abspid)
                           print "adding acid!"
                           sersyringe.write("DIR INF\r")
                           time.sleep(0.15)
                           sersyringe.write("RAT%s\r" % abspid)
                           time.sleep(0.15)
                           sersyringe.write("RUN\r")
                           time.sleep(0.15)
                           sersyringe.write("DIS\r")
                           time.sleep(0.15)
                           #sersyringe.write("DIS\r")
                           #time.sleep(0.1)
                           ivolume=sersyringe.read(100)
                           infusedvolume=ivolume.split("")
                           splitinfuse = infusedvolume[3]
                           splitvals = splitinfuse.split("W")
                           infused = splitvals[0]
                           infusedfloat=re.findall('\d+.\d+',infused)                       
                           #print type(infusedfloat)
                           qqq=''.join(infusedfloat)
                           z=len(qqq)
                           xx=qqq[0:z]
                           #print xx
                           
                           #outputs = str([ph_setpoint,ph_value,infusedfloat,t,"\n"])
                           
                           #text_file = open(filename,"a")
                           #text_file.write(outputs) # write outputs and timestamp to file
                           #text_file.close()
    
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
                                 #print '\n pH = %s'%phval+', time = %s'%t
                             else:
                                 continue
                           except:
                                 continue
                           ph_value=phval
                           
                           if z>0:
                                   voltrack = int(float(xx))
                                   print "Volume infused: " + repr(xx)
                                   diffvoltrack= voltrack-trackvol
                                   if diffvoltrack>= syringevolumemax:
                                           cycles = cycles +1
                                           print "Re-filling syringe!"
                                           print "cycle: %s" % cycles
                                           
                                           sersyringe.write("STP \r")
                                           print "pump stopped"
                                           time.sleep(0.1)
                                           
                                           sersyringe.write("VOL 0 \r")
                                           print "volume set to continous pump"
                                           time.sleep(0.1)
                                           
                                           sersyringe.write("RAT 800.0\r")
                                           print "rate set"
                                           time.sleep(0.1)
                                           
                                           sersyringe.write("DIR REV \r") 
                                           print "direction reversed"
                                           time.sleep(0.1)
                                           
                                           sersyringe.write("VOL %s \r" % syringevolumemax)
                                           print ("volume set to %s" % syringevolumemax)
                                           time.sleep(0.1)
    
                                           sersyringe.write("RUN \r")
                                           print "syringe re-fill..titration will resume shortly..."
    
                                           time.sleep(syringevolumemax*5)
    
                                           sersyringe.write("VOL 0 \r\r")
                                           print "reset pumping to continous"
                                           time.sleep(0.1)
                                           sersyringe.write("DIR REV\r\r")
                                           print "reverse direction and exit loop..."
                                           time.sleep(0.05)                                       
                                           trackvol=trackvol+syringevolumemax
                                   
                           else: print("no value returned from pump")
        except KeyboardInterrupt: #Catch the end of script and reset the pump before quitting the script
            sersyringe.write("STP \r")
            sersyringe.write("RESET* \r")
            sersyringe.close()
            serph.close()
            sys.exit(0)
