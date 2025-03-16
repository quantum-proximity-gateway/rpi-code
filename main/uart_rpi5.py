import serial
import time


class CommunicationTimeoutException(Exception):
    pass


def write_to_pico(username, password):
    ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1) # Specify baud rate and timeout
    try:
        start_time = time.time()
        while True:
            if time.time() - start_time > 10:
                raise CommunicationTimeoutException("Communication timeout after 10 seconds")
                
            json_data = f'{{"username": "{username}", "password": "{password}"}}\n'
            ser.write(json_data.encode())
            response = ser.readline() 
            if response:
                # decode the bytes into a string and strip any trailing newline/carriage return
                try:
                    decoded_response = response.decode('utf-8').strip()
                    print("Received:", decoded_response)
                    if decoded_response == "OK":
                        print('Logged In')
                        return
                except:
                    # Probably received empty bytes - allows program to continue
                    pass    
            time.sleep(1)  # Wait for a second before repeating
    except serial.SerialException as e:
        print(f"Error: {e}")
    except CommunicationTimeoutException as e:
        print(f"Error: {e}")
    finally:
        if ser.is_open:
            ser.close()