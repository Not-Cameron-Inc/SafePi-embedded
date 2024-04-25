#!/usr/bin/python3

import asyncio
import time
from utils import *
from server import run_server

# Function to start the BLE server
async def start_server():
    loop = asyncio.get_event_loop()
    await run(loop)

if __name__ == "__main__":
    # start a thread for device function
    server_thread = threading.Thread(target=device_functions)
    server_thread.start()

    # turn on the BLE server
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_server(loop))
    except KeyboardInterrupt as e:
        print(e)
