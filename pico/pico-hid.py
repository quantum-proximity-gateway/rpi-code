import time
import machine
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# Initialize UART0 with baud rate 9600
uart = machine.UART(0, baudrate=9600)

# Function to send data over UART
def send_data(data):
    uart.write(data)

# Function to receive data over UART
def receive_data():
    if uart.any():
        return uart.read().decode('utf-8')
    return None

username = "Marwan"
password = "helloworld"

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

while True:
    response = receive_data()
    if response:
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