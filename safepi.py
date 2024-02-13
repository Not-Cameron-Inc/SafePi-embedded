#!/usr/bin/python3

import asyncio
from server import run

# Function to start the BLE server
async def start_server():
    loop = asyncio.get_event_loop()
    await run(loop)


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt as e:
        print(e)
