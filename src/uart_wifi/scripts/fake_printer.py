#! python3
"""Fake Anycubic Printer for tests"""
from base64 import decode
import getopt
from queue import Empty
import socket
import sys
import time


class AnycubicSimulator:
    """ "Simulator for Anycubic Printer."""

    port = "6000"
    printing = False
    serial = "0000170300020034"

    def __init__(self, the_ip, the_port, exception_counter_max=5) -> None:
        self.host = the_ip
        self.port = the_port
        self.printing = False
        self.serial = "234234234"
        self.my_socket: socket
        self.exception_counter_max = exception_counter_max
        self.exception_counter = 0

    def sysinfo(self) -> str:
        """return sysinfo type"""
        return "sysinfo,Photon Mono X 6K,V0.2.2," + self.serial + ",SkyNet,end"

    @staticmethod
    def getfile() -> str:
        """return getfile type"""
        return "getfile,Widget.pwmb/0.pwmb,end"

    def getstatus(self) -> str:
        """return getstatus type"""
        if self.printing:
            return (
                "getstatus,print,Widget.pwmb"
                "/46.pwmb,2338,88,2062,51744,6844,~178mL,UV,39.38,0.05,0,end"
            )
        return "getstatus,stop\r\n,end"

    def goprint(self) -> str:
        """Do printing"""
        if self.printing:
            return "goprint,ERROR1,end"
        self.printing = True
        return "goprint,OK,end"

    def gostop(self) -> str:
        """Do Stop printing"""
        if not self.printing:
            return "gostop,ERROR1,end"
        self.printing = False
        return "gostop,OK,end"

    def start_server(self):
        """Start the uart_wifi simualtor server"""
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.my_socket.bind((self.host, self.port))
        self.my_socket.listen(1)
        self.my_socket.setblocking(True)
        while True:
            try:
                conn, addr = self.my_socket.accept()
                print(f"Connected to {addr}")
                decoded_data = ""
                with conn:
                    while True:
                        self.my_socket.setblocking(True)
                        while "," not in decoded_data and "\n" not in decoded_data:
                            data = conn.recv(1)
                            decoded_data += data.decode()
                            if "111\n" in decoded_data:
                                decoded_data = ""
                                continue
                        try:
                            print("Hex:")
                            print(
                                " ".join(
                                    "{:02x}".format(x) for x in decoded_data.encode()
                                )
                            )
                            print("Data:")
                            print(decoded_data)
                        except UnicodeDecodeError:
                            continue
                        split_data = decoded_data.split(",")
                        for split in split_data:
                            if split == "":
                                continue
                            if "getstatus" in split:
                                conn.sendall(self.getstatus().encode())
                            if "sysinfo" in split:
                                conn.sendall(self.sysinfo().encode())
                            if "getfile" in split:
                                conn.sendall(self.getfile().encode())
                            if "goprint" in split:
                                conn.sendall(self.goprint().encode())
                                decoded_data = ""
                            if "gostop" in split:
                                value = self.gostop()
                                print("sent:" + value)
                                conn.sendall(value.encode())
                            if "getmode" in split:
                                value = "getmode,0,end"
                                print("sent:" + value)
                                conn.sendall(value.encode())
                                decoded_data = ""

                            if decoded_data.endswith("shutdown"):
                                self.my_socket.close()
                                self.exception_counter = self.exception_counter_max - 1
                        decoded_data = ""

            except Exception:  # pylint: disable=broad-except
                self.exception_counter += 1
                if self.exception_counter >= self.exception_counter_max:
                    break

            finally:
                time.sleep(1)

    @staticmethod
    def do_shutdown():
        """Shutdown the printer."""
        time.sleep(2.4)


def start_server(the_ip, port, time_idle):
    """Starts the server"""
    AnycubicSimulator(the_ip, int(port), int(time_idle)).start_server()


opts, args = getopt.gnu_getopt(sys.argv, "t:i:p:", ["timeidle=", "ipaddress=", "port="])

IP_ADDRESS = "0.0.0.0"
PORT = 6000
TIME_IDLE = 999999999
for opt, arg in opts:
    if opt in ("-i", "--ipaddress"):
        IP_ADDRESS = arg
    elif opt in ("-p", "--port"):
        PORT = arg
        print("Opening printer on port " + arg)
    elif opt in ("-t", "--timeidle"):
        TIME_IDLE = arg


start_server(IP_ADDRESS, PORT, TIME_IDLE)
