import serial
import time


def write_to_pico(username, password):
    ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1) # Specify baud rate and timeout
    try:
        while True:
            json_data = f'{{"username": "{username}", "password": "{password}"}}\n'
            ser.write(json_data.encode())
            response = ser.readline() 
            if response:
                # decode the bytes into a string and strip any trailing newline/carriage return
                decoded_response = response.decode('utf-8').strip()
                print("Received:", decoded_response)
                if decoded_response == "OK":
                    print('Logged In')
                    return
            time.sleep(1)  # Wait for a second before repeating
    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        if ser.is_open:
            ser.close()
