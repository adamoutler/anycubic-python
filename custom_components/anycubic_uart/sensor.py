"""Platform for sensor integration."""
from __future__ import annotations
from datetime import timedelta
import time
from .base_entry import MonoXEventBase
from .device import AnycubicUartWifiDevice
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import CONF_SERIAL, DEFAULT_STATE, DOMAIN, PRINTER_ICON
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
# _ENTITY_DESCRIPTION = "Mono X Device Sensor"
_AUTO_UPDATE_REASON = "async_update"

SCAN_INTERVAL = timedelta(seconds=15)


async def async_setup(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
):
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
    device = AnycubicUartWifiDevice(hass, entry)

    @callback
    async def async_add_sensor():
        """Add binary sensor from Axis device."""

        the_sensor = MonoXSensor(hass, entry, device)
        async_add_entities([the_sensor])
        entry.async_on_unload(entry.add_update_listener(the_sensor.async_update))
        await the_sensor.async_update()

    entry.async_on_unload(
        async_dispatcher_connect(hass, device.signal_new_event, async_add_sensor)
    )
    await async_add_sensor()


class MonoXSensor(MonoXEventBase, SensorEntity):
    """A simple sensor."""

    # entity_description = _ENTITY_DESCRIPTION
    # entity_description.entity_registry_enabled_default
    # _attr_changed_by = None
    _attr_icon = PRINTER_ICON
    _attr_state = DEFAULT_STATE
    should_poll = True

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, device: AnycubicUartWifiDevice
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, device)
        self.cancel_scheduled_update = None
        self.monox = device.api
        self.entry = entry
        self.hass = hass
        self.entity_id = DOMAIN + "." + device.serial

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        response = self.monox.get_status()
        self._attr_extra_state_attributes = {}

        if response is not None:
            self._attr_native_value = response.status
            self._attr_state = response.status
            if response.total_volume:

                self._attr_extra_state_attributes[
                    _ATTR_PRINTVOL
                ] = response.total_volume.replace("~", "", 1).replace("mL", "", 1)

                self._attr_extra_state_attributes[_ATTR_FILE] = response.file.split(
                    "/", 1
                )

                self._attr_extra_state_attributes[_ATTR_CURLAYER] = int(
                    response.current_layer
                )

                self._attr_extra_state_attributes[_ATTR_TOTALLAYER] = int(
                    response.total_layers
                )
                self._attr_extra_state_attributes[_ATTR_REMLAYER] = int(
                    int(response.total_layers) - int(response.current_layer)
                )
                self._attr_extra_state_attributes[_ATTR_ELAPSEDTIME] = time.strftime(
                    "%H:%M:%S", time.gmtime(int(response.seconds_elapse))
                )
                self._attr_extra_state_attributes[_ATTR_REMAINTIME] = time.strftime(
                    "%H:%M:%S", time.gmtime(int(response.seconds_remaining))
                )

                # self._attr_changed_by = _AUTO_UPDATE_REASON
            else:
                self._attr_extra_state_attributes = []

        self.hass.states.async_set(
            entity_id=self.entity_id,
            new_state=self._attr_state,
            attributes=self._attr_extra_state_attributes,
            force_update=self.force_update,
            context=self._context,
        )

    @callback
    def update_callback(self, no_delay=False):
        """Update the sensor's state, if needed.

        Parameter no_delay is True when device_event_reachable is sent.
        """
        self.hass.add_job(self.async_update_ha_state(self.async_update))

        @callback
        def scheduled_update(now):
            """Timer callback for sensor update."""
            self.cancel_scheduled_update = None
