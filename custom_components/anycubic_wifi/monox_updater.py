"""Utility class to update mono x configuration"""
from .api import MonoXAPI
from .const import (
    CONF_MODEL,
    CONF_SERIAL,
    SW_VERSION,
    UART_WIFI_PORT,
)
from uart_wifi.response import MonoXSysInfo
from homeassistant.const import CONF_HOST, CONF_NAME


def get_monox_info(host: str, data: dict, port: int = 6000) -> None:
    """Gather information from the device, given the IP address"""
    api = MonoXAPI(host, UART_WIFI_PORT)
    sysinfo = api.sysinfo()
    if isinstance(sysinfo, MonoXSysInfo):
        data[CONF_HOST] = host
        map_sysinfo_to_data(sysinfo, data)


def map_sysinfo_to_data(sysinfo: MonoXSysInfo, data: dict) -> None:
    """map the sysInfo result to a dictionary"""
    data[SW_VERSION] = sysinfo.firmware
    data[CONF_MODEL] = sysinfo.model
    data[CONF_NAME] = sysinfo.model
    data[CONF_SERIAL] = sysinfo.serial
