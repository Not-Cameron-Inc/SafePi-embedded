
"""
Example for a BLE 4.0 Server using a GATT dictionary of services and
characteristics
"""

import logging
import asyncio
import threading

from typing import Any, Dict

from bless import (  # type: ignore
        BlessServer,
        BlessGATTCharacteristic,
        GATTCharacteristicProperties,
        GATTAttributePermissions
        )

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)
trigger: threading.Event = threading.Event()


def read_request(
        characteristic: BlessGATTCharacteristic,
        **kwargs
        ) -> bytearray:
    logger.debug(f"Reading {characteristic.value}")
    return characteristic.value


def write_request(
        characteristic: BlessGATTCharacteristic,
        value: Any,
        **kwargs
        ):
    characteristic.value = value
    logger.debug(f"Char value set to {characteristic.value}")
    if characteristic.value == b'\x0f':
        logger.debug("Nice")
        trigger.set()


async def run(loop):
    trigger.clear()

    # Instantiate the server
    gatt: Dict = {
            "a07498ca-ad5b-474e-940d-16f1fbe7e8cd": {
                "51ff12bb-3ed8-46e5-b4f9-d64e2fec021b": {
                    "Properties": (GATTCharacteristicProperties.read |
                                   GATTCharacteristicProperties.write |
                                   GATTCharacteristicProperties.indicate),
                    "Permissions": (GATTAttributePermissions.readable |
                                    GATTAttributePermissions.writeable),
                    "Value": None
                    }
                },
            "5c339364-c7be-4f23-b666-a8ff73a6a86a": {
                "bfc0c92f-317d-4ba9-976b-cc11ce77b4ca": {
                    "Properties": GATTCharacteristicProperties.read,
                    "Permissions": GATTAttributePermissions.readable,
                    "Value": bytearray(b'\x69')
                }
            }
        }
    my_server_name = "SafePi"
    server = BlessServer(name=my_server_name, loop=loop)
    server.read_request_func = read_request
    server.write_request_func = write_request

    await server.add_gatt(gatt)
    await server.start()
    logger.debug(server.get_characteristic(
        "51ff12bb-3ed8-46e5-b4f9-d64e2fec021b"))
    logger.debug("Advertising")
    logger.info("Write '0xF' to the advertised characteristic: " +
                "51ff12bb-3ed8-46e5-b4f9-d64e2fec021b")
    trigger.wait()
    await asyncio.sleep(2)
    logger.debug("Updating")
    server.get_characteristic("51ff12bb-3ed8-46e5-b4f9-d64e2fec021b").value = (
            bytearray(b"i")
            )
    server.update_value(
            "a07498ca-ad5b-474e-940d-16f1fbe7e8cd",
            "51ff12bb-3ed8-46e5-b4f9-d64e2fec021b"
            )
    await asyncio.sleep(5)
    await server.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))