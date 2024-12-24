from bluepy.btle import DefaultDelegate, Scanner, Peripheral, ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM
from dotenv import load_dotenv
import datetime
import os

load_dotenv()
esp_mac_addr = os.getenv("ESP32_MAC_ADDRESS")

SERVICE_UUID = "2246ef74-f912-417f-8530-4a7df291d584"
CHARACTERISTIC_UUID = "a3445e11-5bff-4d2a-a3b1-b127f9567bb6"

class Key():
    def __init__(self, device_name, mac_address, distance):
        self.device_name = device_name
        self.mac_address = mac_address
        self.distance = distance

keys = []
addresses = set()
addresses.add(esp_mac_addr)
# addresses.add("24:ec:4a:02:54:21")
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    
    def handleDiscovery(self, dev, isNewDev, isNewData):
        print(f"Device Seen: {dev.addr}")
        if dev.addr in addresses:
            distance = self.calculateDistance(dev.rssi)
            myKey = Key("", dev.addr, distance)
            print(f"Distance from key: {distance:.2f}")
            mac_address = dev.addr
            try:
                peripheral = Peripheral(mac_address)
                print("CONNECTED!")
                service = peripheral.getServiceByUUID(SERVICE_UUID)
                characteristic = service.getCharacteristics(CHARACTERISTIC_UUID)[0]

                value = characteristic.read().decode("utf-8")
                print(f"Value: {value}")
                peripheral.disconnect()
                print('Disconnected.')
            except Exception as e:
                print(f"Error: {e}")

    
    def calculateDistance(self, rssi):
        '''
            Distance = 10 ^ ((Measured Power -RSSI)/(10 * N))
            Measured Power = RSSI at 1m
            N = Constant from 2-4 depending on Signal Strength
        '''
        return 10 ** ((-40-int(rssi))/(10*4))

count = 0
try:
    while True:

        scanner = Scanner().withDelegate(ScanDelegate())

        print('Scanning for devices...')
        scanner.start(passive=True)
        scanner.process()
        print(f'{count}HERE')
        count += 1
except KeyboardInterrupt:
    scanner.stop()
