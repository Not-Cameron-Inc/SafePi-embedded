import asyncio
from bleak import BleakScanner, BleakClient

async def find_device(char_uuid, data_bytes):
    device = await BleakScanner.find_device_by_name(name='SafePi', timeout=15.0)
    if device is not None:
        print(f'Found SafePi! {device}')
        async with BleakClient(device.address) as client:
            print(client.is_connected)
            input("Pause (press enter)")
            try:
                await client.write_gatt_char(char_uuid, data=data_bytes)
                print("Write successful")
            except Exception as e:
                print(f"Error while writing: {e}")

if __name__ == "__main__":
    data = b'0xf'
    # data_bytes = data.encode('utf-8')
    char_uuid = '51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B' 
    asyncio.run(find_device(char_uuid, data))
