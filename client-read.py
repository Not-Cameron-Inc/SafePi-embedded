import asyncio
from bleak import BleakClient

async def run():
    async with BleakClient("DEVICE_ADDRESS") as client:
        value = await client.read_gatt_char("51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B")
        print("Read value:", value.decode('utf-8'))

asyncio.run(run())
