import logging
import asyncio
from typing import Any, Dict

from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

# Global variable to store the value of the characteristic
characteristic_value = bytearray()


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    logger.debug(f"Reading {characteristic.uuid}: {characteristic_value}")
    return characteristic_value


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    global characteristic_value
    characteristic_value = value
    logger.debug(f"Write request to {characteristic.uuid}: {value}")
    # The value is now stored in characteristic_value, and can be read back by clients


async def run(loop):
    gatt: Dict = {
        "A07498CA-AD5B-474E-940D-16F1FBE7E8CD": {
            "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B": {
                "Properties": GATTCharacteristicProperties.read | GATTCharacteristicProperties.write,
                "Permissions": GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
                "Value": None  # Initial value is empty, will be set by write requests
            }
        }
    }

    server = BlessServer(name="SafePiServer", loop=loop)
    server.read_request_func = read_request
    server.write_request_func = write_request

    await server.add_gatt(gatt)
    await server.start()
    logger.info("Server is now advertising and ready for read/write operations.")

    # Keep the server running
    while True:
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
