"""Utility class to update mono x configuration"""
from config.custom_components.anycubic_uart.const import (
    CONF_MODEL,
    CONF_SERIAL,
    SW_VERSION,
)
from config.custom_components.anycubic_uart.monox import MonoX
from config.custom_components.anycubic_uart.monoxresponse import MonoXSysInfo
from homeassistant.const import CONF_HOST, CONF_NAME


def get_monox_info(host: str, data: dict):
    """Gather information from the device, given the IP address"""
    api = MonoX(host)
    sysinfo = api.get_sysinfo()
    if isinstance(sysinfo, MonoXSysInfo):
        data[CONF_HOST] = host
        map_sysinfo_to_data(sysinfo, data)


def map_sysinfo_to_data(sysinfo: MonoXSysInfo, data: dict):
    """map the sysInfo result to a dictionary"""
    data[SW_VERSION] = sysinfo.firmware
    data[CONF_MODEL] = sysinfo.model
    data[CONF_NAME] = sysinfo.model
    data[CONF_SERIAL] = sysinfo.serial
