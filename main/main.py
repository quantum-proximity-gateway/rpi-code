from bluepy.btle import DefaultDelegate, Scanner, Peripheral
from time import sleep
from threading import Thread
from flask import Flask, jsonify
from flask_cors import CORS
import time
import requests
import logging
import uart_rpi5
from recognise import FaceRecognizer
from pydantic import BaseModel
from encryption_client import EncryptionClient

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
server_url = "https://3ef1-31-205-125-238.ngrok-free.app"

encryption_client = EncryptionClient(server_url)

def reload_encoding():
    response = requests.get(f"{server_url}/encodings", params={'client_id': encryption_client.CLIENT_ID})
    response.raise_for_status()
    response_json = response.json()
    data = encryption_client.decrypt_request(response_json)
    return data

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
 
def get_credentials(mac_address: str, totp: int):
    try:
        data = {
            'mac_address': mac_address,
            'totp': totp
        }
        encrypted_data: dict = encryption_client.encrypt_request(data)
        response = requests.put(f"{server_url}/devices/credentials", json=encrypted_data)
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

                    # Value is the TOTP key
                    value = characteristic.read().decode("utf-8")

                    devices[mac_address]['value'] = int(value)
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

    try:
        while True:
            addresses = set(get_all_mac_addresses()) # change to rescan when dataset retrained?
            data = reload_encoding()
            scanner = Scanner().withDelegate(ScanDelegate())
            print('Scanning for devices...')
            scanner.start(passive=True)
            scanner.process(timeout=3)

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
            if data == {}:
                continue
            face_recognizer = FaceRecognizer(data)
            user_found = face_recognizer.main_loop(filtered_users)

            if user_found is not None:
                mac_address = all_usernames[user_found]
                totp = devices[mac_address]['value']
                username, password = get_credentials(mac_address, totp)
                print("Sending credentials")
                uart_rpi5.write_to_pico(username, password)

                print(f"devices before: {devices}")
                
                # Set user as logged in on the RPi interface
                devices[all_usernames[user_found]]['loggedIn'] = True
                logged_in = all_usernames[user_found]
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
