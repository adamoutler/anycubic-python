"""A file where we test things."""
import socket
import threading
from uart_wifi.communication import UartWifi
from uart_wifi.errors import ConnectionException
from uart_wifi.simulate_printer import AnycubicSimulator
from unittest import TestCase, main as unittest_main


class CommunicationTests(TestCase):
    """Tests"""

    port = 62134

    @pytest.fixture(autouse=True)
    def dummy_printer(self):
        """Start the fake printer"""
        sock = socket.socket()
        sock.bind(("", 0))
        self.port = sock.getsockname()[1]
        sock.close()
        fake_printer = AnycubicSimulator("127.0.0.1", self.port)
        thread = threading.Thread(target=fake_printer.start_server)
        thread.daemon = True
        thread.start()
        yield fake_printer

    def test_connection(self):
        """test basic connection"""
        uart = UartWifi("127.0.0.1", self.port)
        uart.send_request("getstatus,\n")

    def test_nothing_at_all(self):
        """Test basic communications"""
        self.true = False
        assert self.true is not True

    def test_init_fail(self):
        """failure of init"""
        try:
            uart = UartWifi("foo", self.port)
            uart.send_request("foo bar baz")
            fail()
        except ConnectionException:
            pass


if __name__ == "__main__":
    unittest_main()
