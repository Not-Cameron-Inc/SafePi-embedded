import asyncio
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "SafePi"  # The name of your BLE server
CHAR_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"  # The characteristic UUID
DATA_TO_WRITE = b'\x0f'  # The data to write to the characteristic

async def run():
    device = await BleakScanner.find_device_by_name(name='SafePi', timeout=15.0)
    
    if device:
        async with BleakClient(device.address) as client:
            print(f"Connected to {device.name}")
            # Write to the characteristic
            await client.write_gatt_char(CHAR_UUID, DATA_TO_WRITE)
            print(f"Data written to {CHAR_UUID}")
    else:
        print(f"No device with name {DEVICE_NAME} found.")

asyncio.run(run())

