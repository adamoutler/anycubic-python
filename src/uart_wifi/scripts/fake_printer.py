#! python3
"""Fake Anycubic Printer for tests"""
import getopt
import socket
import sys
import time


class AnycubicSimulator:
    """ "Simulator for Anycubic Printer."""

    port = "6000"
    printing = False
    serial = "0000170300020034"

    def __init__(
        self, the_ip: str, the_port: int, exception_counter_max: int = 5
    ) -> None:
        self.host = the_ip
        self.port = the_port
        self.printing = False
        self.serial = "234234234"
        self.my_socket: socket
        self.exception_counter_max = exception_counter_max
        self.exception_counter = 0

    def sysinfo(self) -> str:
        """return sysinfo type"""
        return (
            "sysinfo,Photon Mono X 6K,V0.2.2,"
            + self.serial
            + ",SkyNet,endgetstatus,stop"
        )

    @staticmethod
    def getfile() -> str:
        """return getfile type"""
        return "getfile,Widget.pwmb/0.pwmb,end"

    def getstatus(self) -> str:
        """return getstatus type"""
        if self.printing:
            return (
                "getstatus,print,Phone stand hollow supported.pwmb"
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
        self.my_socket.listen(5)
        while True:
            try:
                conn, addr = self.my_socket.accept()
                data_received = ""
                while not data_received.endswith("\n"):
                    with conn:
                        print(f"Connected to {addr}")
                        data = conn.recv(1024)
                        if not data:
                            break
                        try:
                            print("Hex:")
                            print(" ".join("{:02x}".format(x) for x in data))
                            print("Data:")
                            decoded_data = data.decode()
                            print(decoded_data)
                        except UnicodeDecodeError:
                            continue
                        data_received += decoded_data
                        if data.endswith(("".encode(), "\n".encode())):
                            if data_received.startswith("getstatus"):
                                conn.sendall(self.getstatus().encode())
                            if data_received.startswith("sysinfo"):
                                conn.sendall(self.sysinfo().encode())
                            if data_received.startswith("getfile"):
                                conn.sendall(self.getfile().encode())
                            if data_received.startswith("goprint"):
                                conn.sendall(self.goprint().encode())
                            if data_received.startswith("gostop"):
                                conn.sendall(self.gostop().encode())
                            if data_received.startswith("getmode"):
                                conn.sendall("getmode,0,end".encode())
                            if data_received.endswith("shutdown"):
                                self.my_socket.close()
                                self.exception_counter = self.exception_counter_max - 1

                print(f"Received: {data_received}")
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
TIME_IDLE = 5
for opt, arg in opts:
    if opt in ("-i", "--ipaddress"):
        IP_ADDRESS = arg
    elif opt in ("-p", "--port"):
        PORT = arg
        print("Opening printer on port " + arg)
    elif opt in ("-t", "--timeidle"):
        TIME_IDLE = arg


start_server(IP_ADDRESS, PORT, TIME_IDLE)
