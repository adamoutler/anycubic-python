"""A file where we test things."""
import socket
import threading
import time
import unittest

from pytest import fail

from uart_wifi.communication import UartWifi
from uart_wifi.errors import ConnectionException
from uart_wifi.simulate_printer import AnycubicSimulator
from uart_wifi.response import MonoXResponseType, MonoXStatus


class TestComms(unittest.TestCase):
    """Tests"""

    @classmethod
    def setup_class(cls):
        """Called when setting up the class to start the fake printer"""
        sock = socket.socket()
        sock.bind(("", 0))
        TestComms.port = sock.getsockname()[1]
        sock.close()
        fake_printer = AnycubicSimulator("127.0.0.1", TestComms.port)
        thread = threading.Thread(target=fake_printer.start_server)
        thread.daemon = True
        thread.start()
        print("Sleeping while fake printer starts")
        time.sleep(2)
        print("Fake printer assumed started")

    def test_connection(self):
        """test basic connection"""
        uart = UartWifi("127.0.0.1", TestComms.port)
        uart.send_request("gostop,")
        response: list[MonoXStatus] = uart.send_request("getstatus,\n")
        assert response[0].status == "stop\r\n"
        print(response[0])

    def test_init_fail(self):
        """failure of init"""
        try:
            uart = UartWifi("foo", TestComms.port)
            response = uart.send_request("foo bar baz")
            print(response)
            fail("failure not seen for this request")
        except (ConnectionException, IndexError):
            pass

    @classmethod
    def teardown_class(cls):
        """Called when setting up the class to start the fake printer"""
        uart = UartWifi("127.0.0.1", TestComms.port)
        response: list[MonoXResponseType] = uart.send_request("shutdown,")
        try:
            print(response[0].print())
        except IndexError:
            pass


TestComms.port = 62134
