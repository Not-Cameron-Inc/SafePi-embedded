#!/usr/bin/python3

import asyncio
from utils import *
from server import run

# Function to start the BLE server
async def start_server():
    loop = asyncio.get_event_loop()
    await run(loop)


if __name__ == "__main__":
    # blink or turn on solid LED to indicate whether network is on.
    if internet_on():
        indicator_solid()
    else:
        indicator_blinking()

    # turn on the BLE server
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt as e:
        print(e)
