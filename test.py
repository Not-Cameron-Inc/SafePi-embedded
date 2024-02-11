import asyncio
from bleak import BleakClient

# The BLE server's name; adjust as needed.
SERVER_NAME = "SafePi"
# The UUID of the characteristic you want to write to.
CHAR_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
# The data you want to write to the characteristic.
DATA_TO_WRITE = b'\x0f'

async def run():
    # Use Bleak to discover devices.
    devices = await BleakClient.discover()
    for device in devices:
        if device.name == SERVER_NAME:
            async with BleakClient(device.address) as client:
                # Ensure we're connected to the device.
                if await client.is_connected():
                    print(f"Connected to {device.name}")
                    # Write data to the characteristic.
                    await client.write_gatt_char(CHAR_UUID, DATA_TO_WRITE)
                    print(f"Data written to {CHAR_UUID}")
                    break
    else:
        print(f"No device with name {SERVER_NAME} found.")

asyncio.run(run())
