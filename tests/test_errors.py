"""Tests for errors"""
from uart_wifi.errors import AnycubicException, ConnectionException


def test_commserror():
    """test connection exception"""
    try:
        raise ConnectionException
    except ConnectionException:
        pass


def test_anycubic_exception():
    """Test anycubic exception"""
    try:
        raise AnycubicException
    except AnycubicException:
        pass
