"""MonoX device abstraction."""
from __future__ import annotations

from queue import Empty
from types import MappingProxyType
from typing import Any

from config.custom_components.anycubic_wifi.api import MonoXAPI
from . import monox_updater

from .errors import CannotConnect

import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DOMAIN,
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import (
    ANYCUBIC_3D_PRINTER_NAME,
    ATTR_MANUFACTURER,
    CONF_EVENTS,
    CONF_MODEL,
    CONF_SERIAL,
    CONFIG_FLOW_VERSION,
    DEFAULT_EVENTS,
    DOMAIN,
    PLATFORMS,
    SW_VERSION,
    UART_WIFI_PORT,
)

LOGGER = logging.getLogger(__name__)


class AnycubicUartWifiDevice:
    """Manages a Axis device."""

    #     version: int,
    #     domain: str,
    #     title: str,
    #     data: Mapping[str, Any],
    #     source: str,
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the device."""
        self.hass = hass
        try:
            if config_entry.data is not Empty:
                self.config_entry = config_entry
                self.config_entry.data = dict(self.config_entry.data)
                monox_updater.get_monox_info(
                    self.config_entry.data[CONF_HOST], self.config_entry.data
                )

        except AttributeError:
            self.config_entry = ConfigEntry(
                CONFIG_FLOW_VERSION,
                DOMAIN,
                ANYCUBIC_3D_PRINTER_NAME,
                config_entry,
                DOMAIN,
            )
        if isinstance(self.config_entry.data, MappingProxyType):
            self.config_entry.data = dict(self.config_entry.data)

        if CONF_HOST not in self.config_entry.data:
            self.config_entry.data[CONF_DOMAIN] = DOMAIN
            self.config_entry.data[CONF_MODEL] = None
            self.config_entry.data[CONF_MAC] = None
            self.config_entry.data[CONF_SERIAL] = None
            self.config_entry.data[CONF_HOST] = None
            self.config_entry.data[CONF_PORT] = None
            self.config_entry.data[CONF_NAME] = None
            self.config_entry.data["sw_version"] = "unknown version"

    @property
    def ip_address(self)->str|None:
        """Return the host address of this device."""
        return self.config_entry.data[CONF_HOST]

    @property
    def port(self)->int|str|None:
        """Return the UART_WIFI port of this device."""
        return self.config_entry.data[CONF_PORT]

    @property
    def fw_version(self)->str|None:
        """Return the UART_WIFI port of this device."""
        return self.config_entry.data[SW_VERSION]

    @property
    def model(self)->str|None:
        """Return the model of this device."""
        return self.config_entry.data[CONF_MODEL]

    @property
    def name(self)->str|None:
        """Return the name of this device."""
        return self.config_entry.data[CONF_NAME]

    @property
    def unique_id(self)->str:
        """Return the unique ID (serial number) of this device."""
        return DOMAIN + "." + self.config_entry.data[CONF_SERIAL]

    @property
    def serial(self)->str|None:
        """Return the unique ID (serial number) of this device."""
        return self.config_entry.data[CONF_SERIAL]

    @property
    def mac_address(self)->str|None:
        """Return the mac of this device."""
        return self.config_entry.data[CONF_MAC]

    @property
    def api(self) -> MonoXAPI:
        """Return the unique ID (serial number) of this device."""
        return MonoXAPI(self.config_entry.data[CONF_HOST], UART_WIFI_PORT)

    @property
    def product_type(self) -> str:
        """Return the Product Type of this device."""
        return "3D Printer"

    @property
    def available(self) -> bool:
        """Return the unique ID (serial number) of this device."""
        return True

    def shutdown(self)->None:
        """shutdown method"""
        # do the shutdown

    # Options

    @property
    def option_events(self)->Any:
        """Config entry option defining if platforms based on events should be created."""
        return self.config_entry.options.get(CONF_EVENTS, DEFAULT_EVENTS)

    @property
    def copyright(self)->str:
        """copyright."""
        return "GPLv3"

    @property
    def credits(self)->str:
        """credits."""
        return "Adam Outler <adamoutler@gmail.com>"

    # Callbacks

    @staticmethod
    async def async_new_address_callback(
        hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        """Handle signals of device getting new address.

        Called when config entry is updated.
        This is a static method because a class method (bound method),
        can not be used with weak references.
        """
        device = hass.data[DOMAIN][entry.unique_id]
        device.api.config.host = device.host
        async_dispatcher_send(hass, device.signal_new_address)

    async def async_update_device_registry(self)->None:
        """Update device registry."""
        device_registry = dr.async_get(self.hass)
        device_registry.async_get_or_create(
            config_entry_id=self.config_entry.entry_id,
            identifiers={(DOMAIN, self.unique_id)},
            manufacturer=ATTR_MANUFACTURER,
            model=f"{self.model} {self.product_type}",
            name=self.name,
            sw_version=self.fw_version,
        )

    async def async_setup(self):
        """Set up the device."""
        try:
            if CONF_HOST in self.config_entry.as_dict().keys():
                # we are already setup.
                if self.config_entry.data[CONF_HOST] is not None:
                    self.api = await get_anycubic_device(
                        self.hass, self.config_entry.data[CONF_HOST]
                    )

        except KeyError as err:
            raise ConfigEntryNotReady from err

        async def start_platforms():
            await asyncio.gather(
                *( self.hass.config_entries.async_forward_entry_setup(
                        self.config_entry, platform
                    ) for platform in PLATFORMS
                )
            )

        self.hass.async_create_task(start_platforms())
        self.config_entry.add_update_listener(self.async_new_address_callback)

        return True


def get_anycubic_device(hass, ip_address) -> MonoXAPI | None:
    """Create a Axis device."""

    device = AnycubicUartWifiDevice(hass, {CONF_HOST: ip_address})

    try:
        MonoXAPI(device.ip_address, UART_WIFI_PORT).getstatus()
        return device

    except (asyncio.TimeoutError) as err:
        LOGGER.error("Error connecting to the 3D Printer device at %s", ip_address)
        raise CannotConnect from err
