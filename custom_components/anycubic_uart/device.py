"""Axis network device abstraction."""
from queue import Empty
from types import MappingProxyType
from .anycubic_uart import  monox_updater

from .errors import CannotConnect

import asyncio
import logging
from .monox import MonoX
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
                self.config_entry.data=dict(self.config_entry.data)
                monox_updater.get_monox_info(self.config_entry.data[CONF_HOST],self.config_entry.data)


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

        # unassigned_arps = arp_config.get_unattached_devices(hass)
        # if len(unassigned_arps) > 0:
        #     arp = unassigned_arps[0]
        #     config_entry.data[CONF_HOST] = arp["IP address"]
        #     config_entry.data[CONF_MAC] = arp["HW address"]
        # sysinfo = self.api.get_sysinfo()
        # self.fw_version = sysinfo.firmware
        # config_entry.data[CONF_MODEL] = sysinfo.model
        # config_entry.data[CONF_UNIQUE_ID] = sysinfo.serial

    @property
    def ip_address(self):
        """Return the host address of this device."""
        return self.config_entry.data[CONF_HOST]

    @property
    def port(self):
        """Return the UART_WIFI port of this device."""
        return self.config_entry.data[CONF_PORT]

    @property
    def fw_version(self):
        """Return the UART_WIFI port of this device."""
        return self.config_entry.data[SW_VERSION]

    @property
    def model(self):
        """Return the model of this device."""
        return self.config_entry.data[CONF_MODEL]

    @property
    def name(self):
        """Return the name of this device."""
        return self.config_entry.data[CONF_NAME]

    @property
    def unique_id(self):
        """Return the unique ID (serial number) of this device."""
        return DOMAIN + "." + self.config_entry.data[CONF_SERIAL]

    @property
    def serial(self):
        """Return the unique ID (serial number) of this device."""
        return self.config_entry.data[CONF_SERIAL]

    @property
    def mac_address(self):
        """Return the mac of this device."""
        return self.config_entry.data[CONF_MAC]

    @property
    def api(self) -> MonoX:
        """Return the unique ID (serial number) of this device."""
        return MonoX(self.config_entry.data[CONF_HOST])

    @property
    def product_type(self) -> str:
        """Return the Product Type of this device."""
        return "3D Printer"

    @property
    def available(self) -> MonoX:
        """Return the unique ID (serial number) of this device."""
        return True

    def shutdown(self):
        """shutdown method"""
        # do the shutdown

    # Options

    @property
    def option_events(self):
        """Config entry option defining if platforms based on events should be created."""
        return self.config_entry.options.get(CONF_EVENTS, DEFAULT_EVENTS)

    @property
    def signal_reachable(self):
        """Device specific event to signal a change in connection status."""
        return f"axis_reachable_{self.unique_id}"

    @property
    def signal_new_event(self):
        """Device specific event to signal new device event available."""
        return f"axis_new_event_{self.unique_id}"

    @property
    def signal_new_address(self):
        """Device specific event to signal a change in device address."""
        return f"axis_new_address_{self.unique_id}"

    @property
    def copyright(self):
        """copyright."""
        return "GPLv3"

    @property
    def credits(self):
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

    async def async_update_device_registry(self):
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
                if (self.config_entry.data[CONF_HOST] is not None):
                    self.api = await get_anycubic_device(self.hass, self.config_entry.data[CONF_HOST])


        except KeyError as err:
            raise ConfigEntryNotReady from err

        async def start_platforms():
            await asyncio.gather(
                *(
                    self.hass.config_entries.async_forward_entry_setup(
                        self.config_entry, platform
                    )
                    for platform in PLATFORMS
                )
            )

        @callback
        def async_event_callback(self, action, event_id):
            """Call to configure events when initialized on event stream."""
            if action is not None:
                async_dispatcher_send(self.hass, self.signal_new_event, event_id)

        @callback
        def async_connection_status_callback(self, status):
            """Handle signals of device connection status.

            This is called on every RTSP keep-alive message.
            Only signal state change if state change is true.
            """

        self.hass.async_create_task(start_platforms())
        self.config_entry.add_update_listener(self.async_new_address_callback)

        return True


def get_anycubic_device(hass, ip_address):
    """Create a Axis device."""

    device = AnycubicUartWifiDevice(hass, {CONF_HOST: ip_address})

    try:
        MonoX(device.ip_address).get_status()
        return device

    except (asyncio.TimeoutError) as err:
        LOGGER.error("Error connecting to the 3D Printer device at %s", ip_address)
        raise CannotConnect from err
