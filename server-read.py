import logging
import asyncio
import threading

from typing import Any, Dict

from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    # This is where you define what data is returned when the characteristic is read
    # For example, return a simple string converted to bytes
    data_to_return = "Hello from server".encode('utf-8')
    logger.debug(f"Reading {characteristic.uuid}: {data_to_return}")
    return bytearray(data_to_return)


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    logger.debug(f"Write request to {characteristic.uuid}: {value}")
    # Here you can handle incoming write requests, if needed


async def run(loop):
    gatt: Dict = {
        "A07498CA-AD5B-474E-940D-16F1FBE7E8CD": {
            "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B": {
                "Properties": GATTCharacteristicProperties.read,
                "Permissions": GATTAttributePermissions.readable,
                "Value": None  # Initial value can be set here or returned dynamically in read_request
            }
        }
    }

    server = BlessServer(name="SafePiServer", loop=loop)
    server.read_request_func = read_request
    server.write_request_func = write_request

    await server.add_gatt(gatt)
    await server.start()
    logger.info("Server is now advertising.")

    # Keep the server running
    while True:
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
