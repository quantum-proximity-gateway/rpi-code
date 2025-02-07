import serial
import time

ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1) # Specify baud rate and timeout

try:
    while True:
        ser.write(b'Hello!\n')  # Send data
        time.sleep(1)  # Wait for a second before sending the next message
except serial.SerialException as e:
    print(f"Error: {e}")
finally:
    if ser.is_open:
        ser.close()