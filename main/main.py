from bluepy.btle import DefaultDelegate, Scanner, Peripheral
from time import sleep
from threading import Thread
from flask import Flask, jsonify
from flask_cors import CORS
import time
import subprocess
import json
import requests
import os
import uart_rpi5
from recognise import FaceRecognizer
from pydantic import BaseModel
import pickle
from encryption_client import EncryptionClient

data = None

def reload_encoding():
    global data
    # Load pre-trained face encodings
    print("[INFO] loading encodings...")
    print(os.listdir())
    with open("encodings.pickle", "rb") as f:
        data = pickle.loads(f.read())

app = Flask(__name__)
CORS(app)


# Specific model needed by front-end
class User(BaseModel):
    name: str
    distance: float
    loggedIn: bool


SERVICE_UUID = "2246ef74-f912-417f-8530-4a7df291d584"
CHARACTERISTIC_UUID = "a3445e11-5bff-4d2a-a3b1-b127f9567bb6"

# Security parameters to be tweaked by system administators
TIMEOUT_LIMIT = 60
DISTANCE_LIMIT = 3

devices = {}
logged_in = None
server_url = "https://f3a2-144-82-8-84.ngrok-free.app"

encryption_client = EncryptionClient(server_url)

def get_all_mac_addresses():
    try:
        response = requests.get(f"{server_url}/devices/all-mac-addresses", params={'client_id': encryption_client.CLIENT_ID})
        response.raise_for_status()
        response_json = response.json()
        data = encryption_client.decrypt_request(response_json)
        return [mac.strip() for mac in data['mac_addresses']]
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching MAC addresses: {e}")
        return []
 
def get_credentials(mac_address: str): #TODO: Change to be used only when key validated
    try:
        response = requests.get(f"{server_url}/devices/{mac_address}/credentials", params={'client_id': encryption_client.CLIENT_ID})
        response.raise_for_status()
        data = encryption_client.decrypt_request(response.json())

        return data.get("username", "invalid"), data.get("password", "invalid")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching username for MAC address {mac_address}: {e}")
        return "error"


def get_username_for_mac_address(mac_address: str):
    try:
        response = requests.get(f"{server_url}/devices/{mac_address}/username", params={'client_id': encryption_client.CLIENT_ID})
        response.raise_for_status()
        data = encryption_client.decrypt_request(response.json())

        return data.get("username", "invalid")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching username for MAC address {mac_address}: {e}")
        return "error"

def get_all_usernames(list_mac_addresses: list):
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
            devices[mac_address]['last_seen'] = time.time() # Timestamp for all devices
            if 'loggedIn' not in devices[mac_address]:
                devices[mac_address]['loggedIn'] = False
            if devices[mac_address]['loggedIn'] and distance > DISTANCE_LIMIT: # Log out user when gone (distance 3m>)
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
    global addresses, logged_in

    addresses = set(get_all_mac_addresses())
    try:
        while True:
            scanner = Scanner().withDelegate(ScanDelegate())
            print('Scanning for devices...')
            scanner.start(passive=True)
            scanner.process(timeout=1)

            for device in devices:
                if time.time() - devices[device]['last_seen'] > TIMEOUT_LIMIT: # Delete user if not seen in the last 60 seconds
                    print(device, "has dissapeared.")
                    del devices[device]

            # filter devices by 3m or less
            within_range_mac_addresses = [mac for mac in devices if devices[mac]['distance'] <= 3]
            print(f"within_range_mac_addresses: {within_range_mac_addresses}")

            # get all usernames for each device via mac address from server {username: mac_address}
            all_usernames = get_all_usernames(within_range_mac_addresses)
        
            # Do not check for users already logged in - wastes time
            filtered_users = []
            for username in all_usernames:  
                mac_add = all_usernames[username]
                devices[mac_add]['name'] = username
                if not devices[mac_add]['loggedIn']:
                    filtered_users.append(username)

            # send list of usernames to facial recog script
            face_recognizer = FaceRecognizer(data)
            user_found = face_recognizer.main_loop(filtered_users)

            if user_found is not None:
                print("Sending credentials")
                
                username, password = get_credentials(all_usernames[user_found])
                uart_rpi5.write_to_pico(username, password)

                print(f"devices before: {devices}")
                
                # Set user as logged in on the RPi interface
                devices[all_usernames[user_found]]['loggedIn'] = True
                logged_in = all_usernames[user_found]
                devices[all_usernames[user_found]]['name'] = user_found

                print(f"devices after: {devices}")

    except KeyboardInterrupt:
        scanner.stop()


def check_updates():
    while True:
        current_dir = os.path.dirname(__file__)
        script_path = os.path.join(current_dir, 'update_and_train.sh')
        result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        print(result.stdout)
        if len(result.stdout) > 0:
            reload_encoding()
        print(result.stderr)
        sleep(60)

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
    reload_encoding()
    scan_thread = Thread(target=scan_devices)
    scan_thread.start()
    bash_thread = Thread(target=check_updates)
    bash_thread.start()
    app.run(host='0.0.0.0', port=5000)

# https://prod.liveshare.vsengsaas.visualstudio.com/join?F90D5A054A593F9B4EFFAF49EF458BF4ABA4
