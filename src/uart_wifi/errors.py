"""Exceptions"""


class AnycubicException(Exception):
    """Base class for Anycubic exceptions."""


class ConnectionException(AnycubicException):
    """Problem when connecting"""
