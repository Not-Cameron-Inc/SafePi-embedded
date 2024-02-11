import asyncio
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "SafePi"  # The name of your BLE server
CHAR_UUID = "51ff12bb-3ed8-46e5-b4f9-d64e2fec021b"  # The characteristic UUID
DATA_TO_WRITE = b'\x0f'  # The data to write to the characteristic

async def run():
    device = await BleakScanner.find_device_by_name(name=DEVICE_NAME, timeout=15.0)
    
    if device:
        async with BleakClient(device.address) as client:
            print(f"Connected to {device.name}")
            
            # Discover services and characteristics
            services = await client.get_services()
            characteristic = None
            
            # Find the characteristic by UUID
            for service in services:
                for char in service.characteristics:
                    if char.uuid == CHAR_UUID:
                        characteristic = char
                        break
                if characteristic:
                    break
            
            # Check if the characteristic was found
            if characteristic:
                # Write to the characteristic using the BleakGATTCharacteristic object
                await client.write_gatt_char(characteristic, DATA_TO_WRITE)
                print(f"Data written to {CHAR_UUID}")
            else:
                print(f"Characteristic with UUID {CHAR_UUID} not found.")
    else:
        print(f"No device with name {DEVICE_NAME} found.")

asyncio.run(run())
