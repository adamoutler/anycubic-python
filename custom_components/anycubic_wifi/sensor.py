"""Platform for sensor integration."""
from __future__ import annotations
from curses import has_key
from datetime import timedelta
import datetime
from typing import Any

from .api import MonoXAPI
from .base_entry import AnycubicUartEntityBase
from uart_wifi.response import MonoXStatus
from homeassistant import config_entries

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_UNIQUE_ID, DEVICE_CLASS_TEMPERATURE
from homeassistant.helpers.entity import DeviceInfo
from .const import (
    CONF_MODEL,
    CONF_SERIAL,
    DEFAULT_STATE,
    DOMAIN,
    PRINTER_ICON,
    UART_WIFI_PORT,
)
import logging


from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)
_ATTR_FILE = "file"
_ATTR_PRINTVOL = "print_vol_mL"
_ATTR_CURLAYER = "current_layer_num"
_ATTR_TOTALLAYER = "total_layer_num"
_ATTR_REMLAYER = "remaining_layer_num"
_ATTR_ELAPSEDTIME = "elapsed_time"
_ATTR_REMAINTIME = "remaining_time"

SCAN_INTERVAL = timedelta(seconds=15)


async def async_setup(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
) -> None:
    """The setup method"""
    _LOGGER.debug(entry)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform from config_entry."""
    if entry.unique_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.unique_id] = DOMAIN + entry[CONF_SERIAL]

    @callback
    async def async_add_sensor() -> None:
        """Add binary sensor from Anycubic device."""

        the_sensor = MonoXSensor(hass, entry)
        async_add_entities([the_sensor])
        entry.async_on_unload(entry.add_update_listener(the_sensor.async_update))

    await async_add_sensor()


class MonoXSensor(SensorEntity, AnycubicUartEntityBase):
    """A simple sensor."""

    # _attr_changed_by = None
    _attr_icon = PRINTER_ICON
    _attr_device_class = "3D Printer"
    should_poll = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(entry)
        self.cancel_scheduled_update = None
        self.monox = MonoXAPI(entry.data[CONF_HOST], UART_WIFI_PORT)
        self.entry = entry
        self.hass = hass
        if not self.name:
            self._attr_name = entry.data[CONF_MODEL]

        if not self.unique_id:
            self._attr_unique_id = entry.entry_id
            entry.data[CONF_UNIQUE_ID] = entry.entry_id
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.unique_id)})

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        response: MonoXStatus = self.monox.getstatus()
        self._attr_extra_state_attributes = {}

        if response is not None:
            if hasattr(response,"status"):
                self._attr_native_value = response.status.strip()
                self._attr_state=self._attr_native_value

            if hasattr(response, "current_layer"):
                self.set_attr_int(_ATTR_CURLAYER, int(response.current_layer))
            if hasattr(response, "total_layers"):
                self.set_attr_int(_ATTR_TOTALLAYER, int(response.total_layers))
            if hasattr(response, "current_layer") and hasattr(response, "total_layers"):
                self.set_attr_int(
                    _ATTR_REMLAYER,
                    int(int(response.total_layers) - int(response.current_layer)),
                )
            if hasattr(response, "seconds_elapse"):
                self.set_attr_time(_ATTR_ELAPSEDTIME, int(response.seconds_elapse))
            if hasattr(response, "seconds_remaining"):
                self.set_attr_time(_ATTR_REMAINTIME, int(response.seconds_remaining))
            if hasattr(response, "file"):
                self._attr_extra_state_attributes[_ATTR_FILE] = response.file.split(
                    "/", 1
                )
            if hasattr(response, "total_volume"):
                self.set_attr_int(
                    _ATTR_PRINTVOL,
                    int(response.total_volume.replace("~", "", 1).replace("mL", "", 1)),
                )

        self.hass.states.async_set(
            entity_id=self.entity_id,
            new_state=self._attr_state,
            attributes=self._attr_extra_state_attributes,
            force_update=self.force_update,
            context=self._context,
        )

    async def async_added_to_hass(self):
        """Lifecycle Method when the device is added to HASS"""

    def set_attr_int(self, key: str, value: int) -> None:
        """Handle state attributes"""
        self._attr_extra_state_attributes[key] = int(value)

    def set_attr_time(self, key: str, value: int) -> None:
        """Handle state attributes"""
        self._attr_extra_state_attributes[key] = str(datetime.timedelta(seconds=value))

    @callback
    def update_callback(self, no_delay=False) -> None:
        """Update the sensor's state, if needed.

        Parameter no_delay is True when device_event_reachable is sent.
        """
        self.hass.add_job(self.async_update_ha_state(self.async_update))

        @callback
        def scheduled_update(now):
            """Timer callback for sensor update."""
            self.cancel_scheduled_update = None


@callback
def async_check_significant_change(
    self,
    hass: HomeAssistant,
    old_state: str,
    old_attrs: dict,
    new_state: str,
    new_attrs: dict,
    **kwargs: Any,
) -> bool:
    """Significant Change Support. Insignificant changes are attributes only."""
    if old_state != new_state:
        return True
    return False
