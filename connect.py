import asyncio
from bleak import BleakScanner, BleakClient

async def find_device(char_uuid, data_bytes):
    device = await BleakScanner.find_device_by_name(name='SafePi', timeout=15.0)
    if device is not None:
        print(f'Found SafePi! {device}')
        async with BleakClient(device.address) as client:
            try:
                # Connect to the device
                await client.connect()
                if client.is_connected:
                    print("Connected to SafePi")
                    # Access services property directly after connection
                    print("Services discovered:")
                    for service in client.services:
                        print(service)
                        for char in service.characteristics:
                            print('Characteristics:')
                            print(char)
                            if char.uuid == char_uuid:
                                print(f"Found characteristic {char_uuid}, writing data...")
                                await client.write_gatt_char(char_uuid, data=data_bytes)
                                print("Write successful")
                                break
                    else:
                        print(f"Characteristic {char_uuid} not found.")
                else:
                    print("Failed to connect to SafePi")
            except Exception as e:
                print(f"Error while writing or connecting: {e}")

if __name__ == "__main__":
    data = b'\x0f'  # Make sure your data is in the correct format
    char_uuid = '51ff12bb-3ed8-46e5-b4f9-d64e2fec021b'
    asyncio.run(find_device(char_uuid, data))
