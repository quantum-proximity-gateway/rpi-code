import serial
import time

serial_conn = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)

time.sleep(2)
print("Raspberry Pi 5 UART Initialised")

try:
    while True:
        msg = "Hello from Pi 5"
        serial_conn.write(f"{msg}\r\n".encode('utf-8'))
        print(f"Sent to Pico: {msg}")

        response = serial_conn.readline().decode('utf-8').strip()
        if response:
            print(f"Received from Pico: {response}")
        else:
            print("No response from Pico")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    serial_conn.close()
