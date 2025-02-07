import serial
import time

ser = serial.Serial('/dev/ttyAMA0') # /dev/ttyS3 for UART3 (help...)
while True:
    print(ser.read(5))
    time.sleep(0.1)
