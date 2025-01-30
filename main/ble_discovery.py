from bluepy.btle import DefaultDelegate, Scanner, Peripheral
from time import sleep
from threading import Thread
from flask import Flask, jsonify
import json
import requests
from recognise import main_loop

app = Flask(__name__)

SERVICE_UUID = "2246ef74-f912-417f-8530-4a7df291d584"
CHARACTERISTIC_UUID = "a3445e11-5bff-4d2a-a3b1-b127f9567bb6"

class Key():
    def __init__(self, device_name, mac_address, distance):
        self.device_name = device_name
        self.mac_address = mac_address
        self.distance = distance

keys = []
devices = {}
seenDevices = set()

server_url = "https://2b6a-31-205-125-227.ngrok-free.app"

def get_all_mac_addresses():
    try:
        response = requests.get(f"{server_url}/devices/all-mac-addresses")
        response.raise_for_status()
        mac_addresses = response.json()

        return [mac.strip() for mac in mac_addresses]

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching MAC addresses: {e}")
        return []

def get_username_for_mac_address(mac_address):
    try:
        response = requests.get(f"{server_url}/devices/{mac_address}/username")
        response.raise_for_status()
        data = response.json()

        return data.get("username", "invalid")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching username for MAC address {mac_address}: {e}")
        return "error"

def get_all_usernames(list_mac_addresses):
    usernames = []
    filter_out = ["invalid", "error"]
    
    for mac in list_mac_addresses:
        username = get_username_for_mac_address(mac)
        if username not in filter_out:
            usernames.append(username)

    return usernames

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr in addresses:
            distance = self.calculateDistance(dev.rssi)
            print("Device is " + str(distance) + "m away.")
            print("Device found:", dev.addr, "RSSI:", dev.rssi)
            mac_address = dev.addr
            devices[mac_address] = {}
            distance = self.calculateDistance(dev.rssi)
            devices[mac_address]['distance'] = distance
            print(f"{mac_address} is " + str(distance) + "m away.")
            try:
                with Peripheral(mac_address) as peripheral:
                    print("Device is " + str(distance) + "m away.")
                    print("Connected.")
                    service = peripheral.getServiceByUUID(SERVICE_UUID)
                    characteristic = service.getCharacteristics(CHARACTERISTIC_UUID)[0]
                    value = characteristic.read().decode("utf-8")
                    print(f"Value: {value}")
                    seenDevices.add(mac_address)
                    devices[mac_address]['value'] = json.loads(value)
                    peripheral.disconnect()
                    print("Disconnected.")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                sleep(1)
        

    
    def calculateDistance(self, rssi):
        '''
            Distance = 10 ^ ((Measured Power -RSSI)/(10 * N))
            Measured Power = RSSI at 1m
            N = Constant from 2-4 depending on Signal Strength
        '''
        return 10 ** ((-40-int(rssi))/(10*4))
    
def scan_devices():
    global addresses
    addresses = set(get_all_mac_addresses())
    try:
        while True:
            scanner = Scanner().withDelegate(ScanDelegate())
            print('Scanning for devices...')
            scanner.start(passive=True)
            scanner.process(timeout=5)

            # filter devices by 3m or less
            within_range_mac_addresses = [mac for mac in devices if devices[mac]['distance'] <= 3]
            print(f"within_range_mac_addresses: {within_range_mac_addresses}")

            # get all usernames for each device via mac address from server
            all_usernames = get_all_usernames(within_range_mac_addresses)
            print(f"all_usernames: {all_usernames}")
            
            # send list of usernames to facial recog script
            main_loop(all_usernames)

            # if any username is recognised, send via GPIO to RPi Pico

    except KeyboardInterrupt:
        scanner.stop()

@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify(devices)

if __name__ == '__main__':
    scan_thread = Thread(target=scan_devices)
    scan_thread.start()
    app.run(host='0.0.0.0', port=5000)