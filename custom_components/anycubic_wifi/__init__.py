"""The Anycubic 3D Printer integration."""
from __future__ import annotations
from datetime import timedelta

from .device import AnycubicUartWifiDevice

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN

#  List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]

DOMAIN = "anycubic_wifi"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anycubic 3D Printer from a config entry."""
    # Store an API object for your platforms to access
    hass.data.setdefault(DOMAIN, {})

    device = AnycubicUartWifiDevice(hass, entry)
    if not await device.async_setup():
        return False

    hass.data[DOMAIN][entry.unique_id] = device
    hass.data[DOMAIN][CONF_SCAN_INTERVAL] = timedelta(seconds=15)

    await device.async_update_device_registry()

    #
    return True
    # if CONF_MAC in entry.data and CONF_HOST in entry.data:  # We have a recorded device
    #     # check for IP changes via arp
    #     hass.config_entries.async_setup_platforms(device, PLATFORMS)
    #     await device.async_update_device_registry()
    #     return False

    # hass.data[DOMAIN][entry.unique_id] = device


async def async_update(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    print(entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.unique_id)

    return unload_ok
