"""Tests for the Legrand RFLC component."""
import logging
from typing import Final

import lc7001.aio

from .emulation import Server

_LOGGER: Final = logging.getLogger(__name__)


COMPOSER: Final = lc7001.aio.Composer()


async def test_security_setkey(hass):
    """Test security compliant LC7001 in [SETKEY] mode (factory reset)."""
    sessions = [
        [
            b'[SETKEY]\x00{"MAC":" 0026EC000000"}',
            COMPOSER.wrap(
                1,
                COMPOSER.compose_keys(
                    bytes.fromhex(Server.AUTHENTICATION_OLD),
                    bytes.fromhex(Server.AUTHENTICATION),
                ),
            ),
            b'{"ID":1,"Service":"SetSystemProperties","Status":"Success","ErrorCode":0}\x00',
            COMPOSER.wrap(2, COMPOSER.compose_list_zones()),
            b'{"ID":2,"Service":"ListZones","ZoneList":[],"Status":"Success"}\x00',
        ],
    ]
    await Server(hass, sessions).start()


async def test_security_hello(hass):
    """Test security compliant LC7001 "Hello" challenge."""
    sessions = [
        Server.SECURITY_HELLO_AUTHENTICATION_OK
        + [
            COMPOSER.wrap(1, COMPOSER.compose_list_zones()),
            b'{"ID":1,"Service":"ListZones","ZoneList":[],"Status":"Success"}\x00',
        ],
    ]
    await Server(hass, sessions).start()


async def test_security_non_compliant(hass):
    """Test security non-compliant LC7001 (no authentication)."""
    sessions = [
        [
            Server.SECURITY_NON_COMPLIANT,
            COMPOSER.wrap(1, COMPOSER.compose_list_zones()),
            b'{"ID":1,"Service":"ListZones","ZoneList":[],"Status":"Success"}\x00',
        ],
    ]
    await Server(hass, sessions).start()