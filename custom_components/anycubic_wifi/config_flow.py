"""Config flow for Anycubic 3D Printer."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
import voluptuous as vol

from .api import MonoXAPI

from .device import AnycubicUartWifiDevice
from uart_wifi.response import MonoXResponseType
from .monox_updater import get_monox_info


from homeassistant import config_entries
from homeassistant.components import dhcp
from homeassistant.const import (
    CONF_HOST,
)

from homeassistant.data_entry_flow import FlowResult

from .errors import CannotConnect
from .const import (
    CONF_MODEL,
    CONF_SERIAL,
    DOMAIN,
    UART_WIFI_PORT,
)

LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class MyConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Anycubic config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the Anycubic MonoX config flow."""
        self.device_config = {}
        self.discovery_schema = {}
        self.import_schema = {}
        self.serial = None
        self.data: dict = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a Anycubic MonoX config flow start.

        Manage device specific parameters.
        """
        errors = {}
        if user_input is not None:
            if user_input[CONF_HOST] is not None:
                return await self.process_discovered_device(user_input)
            errors = {"0": "invalid_ip"}
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
        if discovery_info.ip is not None:
            return await self._process_discovered_device({CONF_HOST: discovery_info.ip})

    async def process_discovered_device(
        self, discovered_information: dict
    ) -> FlowResult:
        """Gather information from a discovered device"""
        if discovered_information[CONF_HOST] is not None:
            get_monox_info(discovered_information[CONF_HOST], self.data)
            if CONF_SERIAL in self.data:
                await self.async_set_unique_id(DOMAIN + "." + self.data[CONF_SERIAL])
            else:
                await self.async_set_unique_id(DOMAIN + "." + self.data[CONF_SERIAL])
            self._abort_if_unique_id_configured(
                updates={CONF_HOST: discovered_information[CONF_HOST]}
            )
            return self.async_create_entry(
                title=self.data[CONF_MODEL],
                data=self.data,
                description="Anycubic Uart Device",
            )
        return self.async_abort(reason="ip_not_found")

    async def _process_discovered_device(self, device: dict) -> Any:
        """Prepare configuration for a discovered Axis device."""

        get_monox_info(device[CONF_HOST], dict)
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


def get_anycubic_device(hass, ip) -> AnycubicUartWifiDevice | None:
    """Create an Anycubic device."""

    device = AnycubicUartWifiDevice(hass, {CONF_HOST: ip})

    try:
        return (
            device
            if isinstance(MonoXAPI(ip, UART_WIFI_PORT).sysinfo(), MonoXResponseType)
            else None
        )
    except (asyncio.TimeoutError) as err:
        LOGGER.error("Error connecting to the 3D Printer device at %s", ip)
        raise CannotConnect from err
