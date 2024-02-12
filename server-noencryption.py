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
    message = "Hello from server"
    logger.debug(f"Reading {characteristic.uuid}: {message}")
    return bytearray(message.encode('utf-8')) # currently returning the unencrypted message


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    logger.debug(f"Write request to {characteristic.uuid}: {value}")
    # Here you can handle incoming write requests, if needed
    logger.debug(f"Value Written: {value.decode('utf-8')}")
    

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

    # Keep the server running
    while True:
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))

