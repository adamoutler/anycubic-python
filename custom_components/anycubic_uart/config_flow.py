"""Config flow for Anycubic 3D Printer."""

import asyncio
import logging
import voluptuous as vol

from config.custom_components.anycubic_uart.device import AnycubicUartWifiDevice
from config.custom_components.anycubic_uart.monox import MonoX
from config.custom_components.anycubic_uart.monox_updater import get_monox_info


from . import arp_config
from homeassistant import config_entries
from homeassistant.components import dhcp
from homeassistant.const import (
    CONF_HOST,

)

from homeassistant.data_entry_flow import FlowResult

from .errors import CannotConnect
from homeassistant.core import HomeAssistant
from .const import (
    CONF_MODEL,
    CONF_SERIAL,
    DOMAIN,
    SW_VERSION,
)

LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class MyConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Anycubic config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize the Axis config flow."""
        self.device_config = {}
        self.discovery_schema = {}
        self.import_schema = {}
        self.serial = None
        self.data: dict = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a Axis config flow start.

        Manage device specific parameters.
        """
        errors={}
        if user_input is not None:
            if user_input[CONF_HOST] is not None:
                return self.process_discovered_device(user_input)
            else:
                errors={"0":"invalid_ip"}
        else:

            data = self.discovery_schema or {
                vol.Required(CONF_HOST): str,
            }

            return self.async_show_form(
                step_id="user",
                description_placeholders=user_input,
                data_schema=vol.Schema(data),
                errors=errors,
            )
    async def async_step_dhcp(self, discovery_info: dhcp.DhcpServiceInfo) -> FlowResult:
        """Prepare configuration for a DHCP discovered Anycubic uart-wifi device."""
        if (discovery_info.ip is not None):
            return await self._process_discovered_device(
                {CONF_HOST: discovery_info.ip}
            )
    def process_discovered_device(self,discovered_information:dict)->FlowResult:
        """Gather information from a discovered device"""
        if discovered_information[CONF_HOST] is not None:

            get_monox_info(discovered_information[CONF_HOST],self.data)

            self.async_set_unique_id(DOMAIN + "." + self.data[CONF_SERIAL])

            self._abort_if_unique_id_configured(
                updates={CONF_HOST: discovered_information[CONF_HOST]}
            )
            return self.async_create_entry(
                title=self.data[CONF_MODEL],
                data=self.data,
                description="Anycubic Uart Device",
            )
        else:
            return self.async_abort(reason="ip_not_found")







    async def _process_discovered_device(self, device: dict):
        """Prepare configuration for a discovered Axis device."""

        get_monox_info(device[CONF_HOST],dict)
        await self.async_set_unique_id(DOMAIN + "." + device[CONF_SERIAL])

        self._abort_if_unique_id_configured(
            updates={CONF_HOST: device[CONF_HOST]}, reload_on_update=True
        )

        self.context.update(
            {
                "title_placeholders": {
                    CONF_HOST: device[CONF_HOST],
                },
                "configuration_url": f"http://{device[CONF_HOST]}",
            }
        )

        self.discovery_schema = {
            vol.Required(CONF_HOST, default=device[CONF_HOST]): str,
        }

        return await self.async_step_user()



def _async_has_devices(hass: HomeAssistant) -> bool:
    """Return if there are devices that can be discovered."""
    #  Check if there are any devices that can be discovered in the network.
    devices = arp_config.get_devices_via_arp_table()
    #  we must fix the method of discovery check MAC against recorded
    return len(devices) > 0


class MyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Anycubic Uart device options."""

    def __init__(self, config_entry):
        """Initialize Axis device options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self.device = None

    async def async_step_init(self, user_input=None):
        """Manage the Axis device options."""
        self.device = DOMAIN + "." + self.config_entry[SW_VERSION]
        return await self.async_step_configure_stream()

    async def async_step_configure_stream(self, user_input=None):
        """Manage the Axis device stream options."""
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(title="host", data=self.options)

        schema = {}

        # Stream profiles

        schema[vol.Optional(CONF_HOST, default=self.device)] = vol.In(CONF_HOST)

        return self.async_show_form(
            step_id="configure_stream", data_schema=vol.Schema(schema)
        )


def get_anycubic_device(hass, ip) -> AnycubicUartWifiDevice:
    """Create a Axis device."""

    device = AnycubicUartWifiDevice(hass, {CONF_HOST: ip})

    try:
        MonoX(ip).get_status()
        return device

    except (asyncio.TimeoutError) as err:
        LOGGER.error("Error connecting to the 3D Printer device at %s", ip)
        raise CannotConnect from err
