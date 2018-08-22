import serial
x=serial.Serial(port=2,baudrate=19200,timeout=0.01)
x.write("*RESET \r")
x.close()
x=serial.Serial(port=3,baudrate=9600,timeout=0.01)
x.close()
