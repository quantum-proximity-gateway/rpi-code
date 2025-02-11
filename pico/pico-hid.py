import time
import json
import board
import busio
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# Initialize UART0 with baud rate 115200
uart = busio.UART(board.GP0, board.GP1 ,baudrate=115200, timeout=1)

# Function to send data over UART
def send_data(data):
    uart.write(data)
    print('Sent: ' + data)

# Function to receive data over UART
def receive_data():
    if uart.in_waiting > 0:
        data = uart.read(uart.in_waiting).decode('utf-8')
        print("DATA:" + data)
        try:
            return json.loads(data) # parse json
        except:
            print('invalid data')
    return None

def parse_response(response):
    if 'username' in response and 'password' in response:
        return response['username'], response['password']
    return None, None

'''
    username = "Marwan"
    password = "helloworld"
'''

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

while True:
    send_data('hello\r\n')
    response = receive_data()
    if response:
        username, password = parse_response(response)
        if username and password:
            led.value = True
            keyboard_layout.write(username)
            led.value = False
            keyboard.press(Keycode.ENTER)
            keyboard.release_all()
            time.sleep(2)
            led.value = True
            keyboard_layout.write(password)
            led.value = False
            keyboard.press(Keycode.ENTER)
            keyboard.release_all()
            time.sleep(1)
    time.sleep(1)