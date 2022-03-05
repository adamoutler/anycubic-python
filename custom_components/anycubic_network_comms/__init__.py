"""Anycubic Mono X integration."""
DOMAIN = "monox"


async def async_setup(hass, config):
    hass.states.async_set("hello_state.world", "adam")

    # Return boolean to indicate that initialization was successful.
    return True