"""Handles the API"""
from __future__ import annotations
from typing import Any
from .const import UART_WIFI_PORT
from uart_wifi.communication import UartWifi
from uart_wifi.response import MonoXResponseType, MonoXStatus, MonoXSysInfo


class MonoXAPI(UartWifi):
    """Class for MonoX API calls"""

    def __init__(self, ip_address: str, port: int=UART_WIFI_PORT) -> None:
        the_ip, the_port = get_split(ip_address, port)
        port=int(the_port)
        super().__init__(the_ip, port)
        self.ip_address = the_ip
        self.port = port

    def getstatus(self) -> MonoXResponseType | None:
        """Get the MonoX Status"""
        response = self.send_request("getstatus\r\n")
        return check_monox_response(response, MonoXStatus)

    def sysinfo(self) -> MonoXResponseType | None:
        """Get the MonoX Status"""
        response = self.send_request("sysinfo\r\n")
        return check_monox_response(response, MonoXSysInfo)


def get_split(ip: str, port):
    """Split the ip address from the port"""
    ipsplit = ip.split(":")
    if len(ipsplit) > 1:
        return ipsplit[0], ipsplit[1]
    return str(ipsplit[0]), int(port)


def check_monox_response(
    response: Any, expected: MonoXResponseType
) -> MonoXResponseType | None:
    """Make the response a MonoXResponse type or None at all"""
    return response if isinstance(response, MonoXResponseType) else None
