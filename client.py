#!/usr/bin/python3

import asyncio
from bleak import BleakScanner, BleakClient
from utils import *
import getpass
import argparse


CHAR_UUID_READ = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
CHAR_UUID_WRITE = "52FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"

def run_client(args):
    async def run():
        # Create and start the animation thread
        stop_event = threading.Event()
        animation_thread = threading.Thread(target=wait_animation, args=("Connecting", stop_event))
        animation_thread.start()        

        # Find the SafePi device
        device = await BleakScanner.find_device_by_name(name='SafePi', timeout=20.0)

        # joind the animation thread
        stop_event.set()
        animation_thread.join()

        if device:
            async with BleakClient(device.address) as client:
                print(f"Connected to {device.name}")
                if not args.cli:
                    ssid = input("Please enter wifi network name:")
                    password = getpass.getpass(prompt='Enter your password: ')

                    # define a "wifi" command, so that our server knows to use this to sign into wifi.
                    message = f"{'wifi'} {ssid} {password}"

                    # Reading back the value from the characteristic
                    value = await client.read_gatt_char(CHAR_UUID_READ)
                    print(f"Read from characteristic {CHAR_UUID_READ}: {decrypt(value, '', '')}")
                
                    # Writing to the characteristic
                    encrypted_message = encrypt(message, '', '')
                    print(f"Writing to characteristic {CHAR_UUID_WRITE}: {encrypted_message}")
                    await client.write_gatt_char(CHAR_UUID_WRITE, encrypted_message)
                    print("Write successful")
                else:
                    print('Starting up CLI:')
                    while True:
                        shell_args = input(f'SafePi> ').split()
                        if len(shell_args) < 1:
                            continue
                        command = shell_args[0]
                        if command == 'wifi':
                            if len(shell_args) == 1:
                                shell_args.append(input('Enter SSID:'))
                                shell_args.append(getpass.getpass(prompt='Enter your password: '))
                            await wifi_cmd(client, shell_args)
                        if command == 'read':
                            await read_cmd(client)
                        if command == 'token':
                            if len(shell_args) == 1:
                                shell_args.append(input('Enter token:'))
                            await token_cmd(client, shell_args)
                        if command == 'reboot':
                            await reboot_cmd(client, shell_args)
                        if command == 'write':
                            if len(shell_args) == 1:
                                shell_args.append(input('Enter message:'))
                            await write_cmd(client, shell_args)
                        if command == 'help' or command == '?':
                            menu = f"\nCOMMANDS:\n" \
                                    "help                      -> List commands\n" \
                                    "read                      -> Read from device\n" \
                                    "write <String to write>   -> Writes the string\n" \
                                    "wifi <SSID> <PASSWORD>    -> Sign device onto network\n" \
                                    "token <TOKEN>             -> Write token to authorize device\n" \
                                    "reboot                    -> Reboots the device\n"
                            print(menu)
                        if command == 'exit' or command == 'quit':
                            break
        else:
            print("Device not found")

    asyncio.run(run())

async def wifi_cmd(client, shell_args):
    shell_args.insert('placehold')
    await write_cmd(client, shell_args)

async def read_cmd(client):
    value = await client.read_gatt_char(CHAR_UUID_READ)
    print(f"Read from characteristic {CHAR_UUID_READ}: {decrypt(value, '', '')}")

async def token_cmd(client, shell_args):
    shell_args.insert('placehold')
    await write_cmd(client, shell_args)

async def reboot_cmd(client, shell_args):
    shell_args.insert('placehold')
    await write_cmd(client, shell_args)

async def write_cmd(client, shell_args):
    shell_args.pop(0)
    message = ''
    for arg in shell_args:
        message += f'{arg} '
    encrypted_message = encrypt(message, '', '')
    print(f"Writing to characteristic {CHAR_UUID_WRITE}: {encrypted_message}")
    await client.write_gatt_char(CHAR_UUID_WRITE, encrypted_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bluetooth LE Client')
    parser.add_argument('--cli', '-c', dest='cli', action='store_true', help='Run the CLI')
    
    args = parser.parse_args()
    run_client(args)
