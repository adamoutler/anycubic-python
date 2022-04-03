#! python3
"""Fake Anycubic Printer for tests"""
import getopt

import sys
from uart_wifi.simulate_printer import AnycubicSimulator

def start_server(the_ip: str, port: int) -> None:
    """Starts the server
    :the_ip: The IP address to use internally for opening the port. eg. 127.0.0.1, or 0.0.0.0
    :the_port: The port to monitor for responses.
    """
    AnycubicSimulator(the_ip, int(port)).start_server()


opts, args = getopt.gnu_getopt(sys.argv, "i:p:", ["ipaddress=", "port="])

IP_ADDRESS = "0.0.0.0"
PORT = 6000
for opt, arg in opts:
    if opt in ("-i", "--ipaddress"):
        IP_ADDRESS = arg
    elif opt in ("-p", "--port"):
        PORT = arg
        print("Opening printer on port " + arg)


start_server(IP_ADDRESS, PORT)
