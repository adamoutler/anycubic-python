"""Base classes for MonoX entities."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN


class AnycubicUartEntityBase(Entity):
    """Base common to all MonoX entities."""

    def __init__(self, device):
        """Initialize the MonoX event."""
        self.device = device

        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device.unique_id)})

    async def async_added_to_hass(self):
        """Subscribe device events."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self.device.signal_reachable, self.update_callback
            )
        )

    @property
    def available(self):
        """Return True if device is available."""
        return self.device.available

    @callback
    def update_callback(self, no_delay=None):
        """Update the entities state."""
        self.async_write_ha_state()


class MonoXEventBase(AnycubicUartEntityBase):
    """Base common to all Axis entities from event stream."""

    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, device):
        """Initialize the Axis event."""
        super().__init__(device)
        self.entry = entry

        self._attr_name = f"{device.model}"
        self._attr_unique_id = f"{DOMAIN}.{device.serial}"

    async def async_added_to_hass(self) -> None:
        """Subscribe sensors events."""

        await super().async_added_to_hass()

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect device object when removed."""
