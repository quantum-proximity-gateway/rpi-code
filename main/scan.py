from bluepy.btle import DefaultDelegate, Scanner, Peripheral
import time
import logging
from time import sleep
from recognise import FaceRecognizer
import requests
import uart_rpi5
from encryption_client import EncryptionClient

SERVICE_UUID = "2246ef74-f912-417f-8530-4a7df291d584"
CHARACTERISTIC_UUID = "a3445e11-5bff-4d2a-a3b1-b127f9567bb6"

TIMEOUT_LIMIT = 60
DISTANCE_LIMIT = 3
STRIKE_LIMIT = 5

server_url = "https://3a44-31-205-125-238.ngrok-free.app"
encryption_client = EncryptionClient(server_url)

devices = {}

def reload_encoding():
    try:
        response = requests.get(
            f"{server_url}/encodings", 
            params={'client_id': encryption_client.CLIENT_ID}
        )
        response.raise_for_status()
        response_json = response.json()
        data = encryption_client.decrypt_request(response_json)
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while fetching encodings: {e}")
        return {}

def get_all_mac_addresses():
    try:
        response = requests.get(
            f"{server_url}/devices/all-mac-addresses", 
            params={'client_id': encryption_client.CLIENT_ID}
        )
        response.raise_for_status()
        response_json = response.json()
        data = encryption_client.decrypt_request(response_json)
        return [mac.strip() for mac in data['mac_addresses']]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while fetching MAC addresses: {e}")
        return []

def get_username_for_mac_address(mac_address: str):
    try:
        response = requests.get(
            f"{server_url}/devices/{mac_address}/username", 
            params={'client_id': encryption_client.CLIENT_ID}
        )
        response.raise_for_status()
        data = encryption_client.decrypt_request(response.json())
        return data.get("username", "invalid")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching username for MAC address {mac_address}: {e}")
        return "error"

def get_all_usernames(list_mac_addresses: list):
    usernames = {}
    filter_out = ["invalid", "error"]
    for mac in list_mac_addresses:
        username = get_username_for_mac_address(mac)
        if username not in filter_out:
            usernames[username] = mac
    return usernames

def get_credentials(mac_address: str, totp: int):
    try:
        data = {'mac_address': mac_address, 'totp': totp}
        encrypted_data = encryption_client.encrypt_request(data)
        response = requests.put(f"{server_url}/devices/credentials", json=encrypted_data)
        response.raise_for_status()
        data = encryption_client.decrypt_request(response.json())
        return data.get("username", "invalid"), data.get("password", "invalid")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching credentials for MAC address {mac_address}: {e}")
        

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        super().__init__()
    
    def handleDiscovery(self, dev, isNewDev, isNewData):
        global devices, addresses
        if dev.addr in addresses:
            distance = self.calculateDistance(dev.rssi)
            logging.info(f"{dev.addr} is {distance}m away.")
            mac_address = dev.addr
            if mac_address not in devices:
                devices[mac_address] = {'loggedIn': False, 'name': None, 'strikes': 0}
            devices[mac_address]['last_seen'] = time.time()

            if devices[mac_address]['loggedIn'] and distance > DISTANCE_LIMIT:
                if devices[mac_address]['strikes'] < STRIKE_LIMIT:
                    devices[mac_address]['strikes'] += 1
                else:
                    devices[mac_address]['loggedIn'] = False
            elif devices[mac_address]['loggedIn'] and distance < DISTANCE_LIMIT:
                devices[mac_address]['strikes'] = 0

            devices[mac_address]['distance'] = distance
            try:
                with Peripheral(mac_address) as peripheral:
                    logging.info("Connected.")
                    service = peripheral.getServiceByUUID(SERVICE_UUID)
                    characteristic = service.getCharacteristics(CHARACTERISTIC_UUID)[0]
                    value = characteristic.read().decode("utf-8")
                    devices[mac_address]['value'] = int(value)
                    peripheral.disconnect()
                    logging.info("Disconnected.")
            except Exception as e:
                logging.error(f"Error: {e}")
            finally:
                sleep(1)
        
    def calculateDistance(self, rssi):
        '''
            Distance = 10 ^ ((Measured Power -RSSI)/(10 * N))
            Measured Power = RSSI at 1m
            N = Constant from 2-4 depending on Signal Strength
        '''
        return 10 ** ((-40 - int(rssi)) / (10 * 4))

def scan_devices():
    global addresses, devices
    while True:
        addresses = set(get_all_mac_addresses())
        data = reload_encoding()
        
        scanner = Scanner().withDelegate(ScanDelegate())
        logging.info("Scanning for devices...")
        
        try:
            scanner.start(passive=True)
            scanner.process(timeout=3)
        except Exception as e:
            logging.error(f"Error during device scanning: {e}")
            # Continue with the next iteration if scanning fails
            sleep(1)
            continue
        
        for dev in list(devices):
            if time.time() - devices[dev]['last_seen'] > TIMEOUT_LIMIT:
                print(dev, "has disappeared.")
                del devices[dev]
        
        within_range_mac_addresses = [
            mac for mac in devices if devices[mac].get('distance', float('inf')) <= DISTANCE_LIMIT
        ]
        all_usernames = get_all_usernames(within_range_mac_addresses)
        
        filtered_users = []
        for username in all_usernames:
            mac_add = all_usernames[username]
            devices[mac_add]['name'] = username
            if not devices[mac_add]['loggedIn']:
                filtered_users.append(username)
        
        if not data:
            logging.warning("No facial encoding data available, skipping face recognition")
            sleep(1)
            continue
        
        try:
            face_recognizer = FaceRecognizer(data)
            user_found = face_recognizer.main_loop(filtered_users)
        except Exception as e:
            logging.error(f"Error during face recognition: {e}")
            user_found = None
        
        if user_found is not None:
            mac_address = all_usernames[user_found]
            totp = devices[mac_address]['value']
            username, password = get_credentials(mac_address, totp)
            if username == "invalid" or password == "invalid":
                logging.error("Failed to get valid credentials.")
                continue
            
            try:
                logging.warning("Sending credentials to Pico")
                uart_rpi5.write_to_pico(username, password)
                devices[mac_address]['loggedIn'] = True
                devices[mac_address]['name'] = user_found
            except Exception as e:
                logging.error(f"Error sending credentials to Pico: {e}")