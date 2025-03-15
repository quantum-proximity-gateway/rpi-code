from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread
import logging
import coloredlogs
from pydantic import BaseModel

# Import the scan functionality and shared devices dictionary
from scan import scan_devices, devices

app = Flask(__name__)
CORS(app)
coloredlogs.install(level='INFO', fmt='%(asctime)s - %(levelname)s - %(message)s')

class User(BaseModel):
    name: str
    distance: float
    loggedIn: bool

@app.route('/api/devices', methods=['GET'])
def get_devices():
    users = []
    for device in devices:
        users.append({
            "name": devices[device]['name'],
            "distance": devices[device]['distance'],
            "loggedIn": devices[device]['loggedIn']
        })
    validated_users = [User(**user).dict() for user in users]
    return jsonify(validated_users)

if __name__ == '__main__':
    scan_thread = Thread(target=scan_devices)
    scan_thread.start()
    app.run(host='0.0.0.0', port=5000)