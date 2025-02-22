from bluepy.btle import DefaultDelegate, Scanner, Peripheral
from time import sleep
from threading import Thread
from flask import Flask, jsonify
from flask_cors import CORS
import json
import requests
from recognise import main_loop
from pydantic import BaseModel

app = Flask(__name__)
CORS(app)

# Specific model needed by front-end
class User(BaseModel):
    name: str
    distance: float
    loggedIn: bool

SERVICE_UUID = "2246ef74-f912-417f-8530-4a7df291d584"
CHARACTERISTIC_UUID = "a3445e11-5bff-4d2a-a3b1-b127f9567bb6"


devices = {}
server_url = "https://bf6c-144-82-8-152.ngrok-free.app"

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
    usernames = {} # usernames assumed to be unique in an organisation
    filter_out = ["invalid", "error"]
    
    for mac in list_mac_addresses:
        username = get_username_for_mac_address(mac)
        if username not in filter_out:
            usernames[username] = mac

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
            if mac_address not in devices:
                devices[mac_address] = {}
            devices[mac_address]['loggedIn'] = False
            distance = self.calculateDistance(dev.rssi)
            devices[mac_address]['distance'] = distance
            print(f"{mac_address} is " + str(distance) + "m away.")
            try:
                with Peripheral(mac_address) as peripheral:
                    print("Device is " + str(distance) + "m away.")
                    print("Connected.")

                    # Set as the same service and characteristics for each device
                    service = peripheral.getServiceByUUID(SERVICE_UUID)
                    characteristic = service.getCharacteristics(CHARACTERISTIC_UUID)[0]

                    # Value is the OTP key {key: Key, mac_address: mac_address}
                    value = characteristic.read().decode("utf-8")
                    print(f"Value: {value}")

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
            print(f"all_usernames: {all_usernames.keys()}")
            
            # send list of usernames to facial recog script
            user_found = main_loop(all_usernames.keys())
            if user_found is not None:
                print("goes here")
                # TODO: Get the credentials and send to RPi Pico

                print(f"devices before: {devices}")
                
                # Set user as logged in on the RPi interface
                devices[all_usernames[user_found]]['loggedIn'] = True
                devices[all_usernames[user_found]]['name'] = user_found

                print(f"devices after: {devices}")

    except KeyboardInterrupt:
        scanner.stop()


@app.route('/api/devices', methods=['GET'])
def get_devices():
    print(devices)
    users = []
    for device in devices:
        print(f"device: {device}")
        users.append({"name": devices[device]['name'], "distance":devices[device]['distance'],"loggedIn": devices[device]['loggedIn'] })
    validated_users = [User(**user).dict() for user in users]
    return jsonify(validated_users)

if __name__ == '__main__':
    scan_thread = Thread(target=scan_devices)
    scan_thread.start()
    app.run(host='0.0.0.0', port=5000)
# https://prod.liveshare.vsengsaas.visualstudio.com/join?E4D365FE5CB55AE8BF230FB790BA5E17D550
