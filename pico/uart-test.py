import machine
import utime

# Initialize UART with the appropriate pins and baud rate
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

while True:
    if uart.any():
        data = uart.read(5)  # Read up to 5 bytes
        if data:
            print(data)
    utime.sleep(0.1)