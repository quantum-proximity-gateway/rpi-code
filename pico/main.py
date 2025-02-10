import machine
import time

uart = machine.UART(0, tx=machine.Pin(0), rx=machine.Pin(1), baudrate=115200)
led = machine.Pin("LED", machine.Pin.OUT)

print("Pico UART Initialised")

while True:
    
    if uart.any():
        received = uart.read().decode("UTF-8")
        print(f"Received from Pi 5: {received}")
        uart.write(f"Echo: {received}\r\n")
    
    led.toggle()
 
    time.sleep(1)