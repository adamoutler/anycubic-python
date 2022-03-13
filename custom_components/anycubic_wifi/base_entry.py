"""Base classes for MonoX entities."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity


class AnycubicUartEntityBase(Entity):
    """Base common to all MonoX entities."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the MonoX event."""
        self.entry = entry

    async def async_added_to_hass(self) -> None:
        """Subscribe device events."""
        self.async_on_remove(
            async_dispatcher_connect(self.hass, "unload", self.update_callback)
        )

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        return True

    @callback
    def update_callback(self, no_delay=None) -> None:
        """Update the entities state."""
        self.async_write_ha_state()
