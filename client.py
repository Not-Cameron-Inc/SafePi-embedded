import asyncio
from bleak import BleakScanner, BleakClient
from utils import *

CHAR_UUID_READ = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
CHAR_UUID_WRITE = "52FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
DATA_TO_WRITE = b'Hello from client'  # Data to write to the characteristic

async def run():
    # Find the device by its advertised name
    device = await BleakScanner.find_device_by_name(name='SafePi', timeout=20.0)
    
    if device:
        async with BleakClient(device.address) as client:
            print(f"Connected to {device.name}")

            # Reading back the value from the characteristic
            value = await client.read_gatt_char(CHAR_UUID_READ)
            print(f"Read from characteristic {CHAR_UUID_READ}: {decrypt(value, '', '')}")

            # Writing to the characteristic
            ssid = input("Please enter wifi network name:")
            password = input("Enter wifi password:")
            message = f'{ssid} {password}'
            encrypted_message = encrypt(message, '', '')
            print(f"Writing to characteristic {CHAR_UUID_WRITE}: {encrypted_message}")
            await client.write_gatt_char(CHAR_UUID_WRITE, encrypted_message)
            print("Write successful")

    else:
        print("Device not found")

asyncio.run(run())
