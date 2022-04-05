"""A file where we test things."""
import socket
import threading
from unittest import TestCase, main as unittest_main
import unittest
import pytest
from pytest import fail

from uart_wifi.communication import UartWifi
from uart_wifi.errors import ConnectionException
from uart_wifi.simulate_printer import AnycubicSimulator


# class CommunicationTests(TestCase):
#     """Tests"""

#     port = 62134
#     # if __name__ == "__main__":
#     #     suite = unittest.TestSuite()
#     #     suite.addTest(TestCase("test_nothing_at_all"))
#     #     suite.addTest(TestCase("test_connection"))
#     #     suite.addTest(TestCase("test_init_fail"))

#     #     unittest.TextTestRunner().run(suite)

#     def __init__(self, testname, methodName):
#         """init"""
#         unittest.TestCase.__init__(self, methodName=methodName)

#         self.true: bool = True

#     @pytest.fixture(autouse=True)
#     def dummy_printer(self):
#         """Start the fake printer"""
#         sock = socket.socket()
#         sock.bind(("", 0))
#         self.port = sock.getsockname()[1]
#         sock.close()
#         fake_printer = AnycubicSimulator("127.0.0.1", self.port)
#         thread = threading.Thread(target=fake_printer.start_server)
#         thread.daemon = True
#         thread.start()
#         yield fake_printer

#     def test_connection(self):
#         """test basic connection"""
#         uart = UartWifi("127.0.0.1", self.port)
#         uart.send_request("getstatus,\n")

#     def test_nothing_at_all(self):
#         """Test basic communications"""
#         self.true = False
#         assert self.true is not True

#     def test_init_fail(self):
#         """failure of init"""
#         try:
#             uart = UartWifi("foo", self.port)
#             uart.send_request("foo bar baz")
#             fail()
#         except ConnectionException:
#             pass


# if __name__ == "__main__":
#     unittest_main()
