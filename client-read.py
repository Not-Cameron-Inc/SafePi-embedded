import asyncio
from bleak import BleakScanner, BleakClient

async def run():
    device = await BleakScanner.find_device_by_name(name='SafePiServer', timeout=15.0)
    if device:
        async with BleakClient(device.address) as client:
            await client.connect()
            value = await client.read_gatt_char("51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B")
            print("Read value:", value.decode('utf-8'))
    else:
        print("Device not found")

asyncio.run(run())

