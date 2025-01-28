import serial

ser = serial.Serial('/dev/ttyAMA0') # /dev/ttyS3 for UART3 (help...)
ser.write(b'username\n') # send username
ser.write(b'password\n') # send password
ser.close()
