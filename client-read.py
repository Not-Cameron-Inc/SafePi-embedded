import asyncio
from bleak import BleakClient, BleakScanner

CHAR_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
DATA_TO_WRITE = b'Hello from client'

async def run():
    device = await BleakScanner.find_device_by_name(name='SafePiServer', timeout=15.0)
    if device:
        async with BleakClient(device.address) as client:
            # Writing to the characteristic
            print(f"Writing to characteristic {CHAR_UUID}: {DATA_TO_WRITE}")
            await client.write_gatt_char(CHAR_UUID, DATA_TO_WRITE)
            print("Write successful")

            # Reading back the written value
            value = await client.read_gatt_char(CHAR_UUID)
            print(f"Read from characteristic {CHAR_UUID}: {value.decode('utf-8')}")

    else:
        print("Device not found")

asyncio.run(run())
