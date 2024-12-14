from bluepy.btle import Scanner, DefaultDelegate

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        super().__init__()
    
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print(f"Discovered new device: {dev.addr}")
        elif isNewData:
            print(f"Received new data from device: {dev.addr}")

scanner = Scanner().withDelegate(ScanDelegate())
print('Scanning for devices...')
devices = scanner.scan(20.0)

for dev in devices:
    print(f"Device: {dev.addr}, RSSI: {dev.rssi} dBm")
    for (adtype, desc, value) in dev.getScanData():
        print(f"  {desc}: {value}")