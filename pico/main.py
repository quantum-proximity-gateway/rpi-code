import machine
import time

uart = machine.UART(0, tx=machine.Pin(0), rx=machine.Pin(1), baudrate=9600)
led = machine.Pin("LED", machine.Pin.OUT)

print("Pico UART Initialised")
led.toggle()

while True:
    uart.write("Send from Pico\r\n")
    print("Sent Pico msg")
    
    try:
       data = uart.read()
       if data:
           print("Data found")
           data = data.decode('utf-8')
           print(f"Received from Pi 5: {data}")
           uart.write(f"Echo: {data}\r\n")
       else:
           print(f"No data: {data}")
        
    except Exception as e:
       print(f"Error: {e}")
    
    time.sleep(2)