from homeassistant import config_entries
from .const import DOMAIN
from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntry
from homeassistant.core import HomeAssistant
from . import api


class ExampleConfigFlow(config_entries.ConfigFlow, domain=monox):
    async def async_step_user(self, info):
        if info is not None:
            pass  # TODO: process info
        unique_id = user_input["unique_id"]
        await self.async_set_unique_id(unique_id)
        return self.async_show_form(
            step_id="ip", data_schema=vol.Schema({vol.Required("password"): str})
        )
        
    async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
        """Setup up a config entry."""

        # TODO: Replace with actual API setup and exception
        auth = api.AsyncConfigEntryAuth(...)
        try:
            await auth.refresh_tokens()
        except TokenExpiredError as err:
            raise ConfigEntryAuthFailed(err) from err