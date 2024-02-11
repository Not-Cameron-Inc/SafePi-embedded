import asyncio
from bleak import BleakScanner, BleakClient

CHAR_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"  # The characteristic UUID for both read and write
DATA_TO_WRITE = b'Hello from client'  # Data to write to the characteristic

async def run():
    # Find the device by its advertised name
    device = await BleakScanner.find_device_by_name(name='SafePiServer', timeout=20.0)
    
    if device:
        async with BleakClient(device.address) as client:
            print(f"Connected to {device.name}")

            # Writing to the characteristic
            print(f"Writing to characteristic {CHAR_UUID}: {DATA_TO_WRITE}")
            await client.write_gatt_char(CHAR_UUID, DATA_TO_WRITE)
            print("Write successful")

            # Reading back the value from the characteristic
            value = await client.read_gatt_char(CHAR_UUID)
            print(f"Read from characteristic {CHAR_UUID}: {value}")

    else:
        print("Device not found")

asyncio.run(run())
