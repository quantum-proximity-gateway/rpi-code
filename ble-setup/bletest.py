from bluepy.btle import Scanner, Peripheral, ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM

SERVICE_UUID = "2246ef74-f912-417f-8530-4a7df291d584"
CHARACTERISTIC_UUID = "a3445e11-5bff-4d2a-a3b1-b127f9567bb6"
scanner = Scanner()
print('Scanning for devices...')
devices = scanner.scan(10.0, passive=True) # Passive helps for RPI
addresses = set()
addresses.add("24:ec:4a:02:54:21")
for dev in devices:
    if dev.addr in addresses:
        '''
            Distance = 10 ^ ((Measured Power -RSSI)/(10 * N))
            Measured Power = RSSI at 1m
            N = Constant from 2-4 depending on Signal Strength
        '''
        distance = 10 ** ((-40-int(dev.rssi))/(10*4))
        print(f"Distance from key: {distance:.2f}")
        print(dev.addrType)
        mac_address = dev.addr
        try:
            peripheral = Peripheral(mac_address, addrType=ADDR_TYPE_RANDOM)
        except Exception as e:
            print(f"Error: {e}")
        break
