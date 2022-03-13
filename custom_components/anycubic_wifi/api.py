"""Handles the API"""
from __future__ import annotations
from typing import Any
from uart_wifi.communication import UartWifi
from uart_wifi.response import MonoXResponseType, MonoXStatus, MonoXSysInfo

class MonoXAPI(UartWifi):
    """Class for MonoX API calls"""

    def __init__(self, ip_address: str, port: int) -> None:
        super().__init__(ip_address, port)
        self.ip_address = ip_address
        self.port = port

    def getstatus(self) -> MonoXResponseType | None:
        """Get the MonoX Status"""
        response = self.send_request(__name__)
        return check_monox_response(response,MonoXStatus)

    def sysinfo(self) -> MonoXResponseType | None:
        """Get the MonoX Status"""
        response = self.send_request(__name__)
        return check_monox_response(response,MonoXSysInfo)


def check_monox_response(response:Any,expected:MonoXResponseType) -> MonoXResponseType | None:
    """Make the response a MonoXResponse type or None at all"""
    return response if isinstance(response, MonoXResponseType) else None
