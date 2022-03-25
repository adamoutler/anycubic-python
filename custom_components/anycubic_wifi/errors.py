"""Errors for the Axis component."""
from homeassistant.exceptions import HomeAssistantError


class AnycubicException(HomeAssistantError):
    """Base class for Axis exceptions."""


class AnycubicMonoXAPILevel(AnycubicException):
    """Problem with API."""


class AlreadyConfigured(AnycubicException):
    """Device is already configured."""


class CannotConnect(AnycubicException):
    """Unable to connect to the device."""


class UserLevel(AnycubicException):
    """User level too low."""
