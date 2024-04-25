#!/usr/bin/python3

import logging
import asyncio

from utils import *
from typing import Any, Dict
from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    # This is where we define what data is returned when the characteristic is read
    # For example, return a simple string converted to bytes"

    message = CONNECTION_STATUS
    encrypted_message = encrypt(message, '', '')

    client_info = kwargs.get('client_identifier', 'Unknown')  # Adjust based on actual available data
    logger.debug(f"Read request from {kwargs} for {characteristic.uuid}: {encrypted_message}")
    logger.debug(f"Reading {characteristic.uuid}: {encrypted_message}")
    return bytearray(encrypted_message)


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    logger.debug(f"Write request to {characteristic.uuid}: {value}")
    # log the decrypted write
    message = decrypt(value, AES_KEY, IV)
    logger.debug(f'Decrypted: {message}')
    # send the data to be handled. 
    handle_write(message)
    
    
async def run(loop):
    #define a GATT server with one service and two characteristics. One for reading, and the other for writing.
    gatt: Dict = {
        "A07498CA-AD5B-474E-940D-16F1FBE7E8CD": {
            "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B": {
                "Properties": GATTCharacteristicProperties.read,
                "Permissions": GATTAttributePermissions.readable,
                "Value": None  # Initial value can be set here or returned dynamically in read_request
            },
            "52FF12BB-3ED8-46E5-B4F9-D64E2FEC021B": {
                "Properties": GATTCharacteristicProperties.write,
                "Permissions": GATTAttributePermissions.writeable,
                "Value": None  # Initial value can be set here or returned dynamically in read_request
            }
        }
    }

    server = BlessServer(name="SafePi", loop=loop)
    server.read_request_func = read_request
    server.write_request_func = write_request

    # add our GATT server and start it.
    await server.add_gatt(gatt)
    await server.start()
    logger.info("Server is now advertising.")

    # start up the device functions
    device_functions()

    # Keep the server running
    while True:
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))


