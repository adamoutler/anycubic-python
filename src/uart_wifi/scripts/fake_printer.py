#! python3
"""Fake Anycubic Printer for tests"""
import getopt
import select
import socket
import sys
import threading
import time


class AnycubicSimulator:
    """ "Simulator for Anycubic Printer."""

    port = "6000"
    printing = False
    serial = "0000170300020034"
    shutdown_signal = False

    def __init__(self, the_ip, the_port) -> None:
        self.host = the_ip
        self.port = the_port
        self.printing = False
        self.serial = "234234234"

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
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.bind((self.host, self.port))
        my_socket.listen(1)
        my_socket.setblocking(False)
        read_list = [my_socket]
        while not AnycubicSimulator.shutdown_signal:
            readable, [], [] = select.select(read_list, [], [])
            for s in readable:
                if s is my_socket:
                    try:
                        conn, addr = my_socket.accept()
                        thread = threading.Thread(
                            target=self.response_selector,
                            args=(conn, addr),
                        )
                        thread.setDaemon(True)
                        thread.start()
                    except Exception:  # pylint: disable=broad-except
                        pass
                    finally:
                        time.sleep(1)

    def response_selector(self, conn, addr):
        """The connection handler"""
        print(f"Connected to {addr}")
        decoded_data = ""
        with conn:
            while not AnycubicSimulator.shutdown_signal:
                while "," not in decoded_data and "\n" not in decoded_data:
                    data = conn.recv(1)
                    decoded_data += data.decode()
                    if "111\n" in decoded_data:
                        decoded_data = ""
                        continue
                try:
                    print("Hex:")
                    print(" ".join(f"{hex:02x}" for hex in decoded_data.encode()))
                    print("Data:")
                    print(decoded_data)
                except UnicodeDecodeError:
                    continue
                self.send_response(conn, decoded_data)
                decoded_data = ""

    def send_response(self, conn, decoded_data):
        """Send a response"""
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
            if "incomplete" in split:
                value = "getmode,0,"
                print("sent:" + value)
                conn.sendall(value.encode())
                decoded_data = ""
            if "multi" in split:
                value = self.getstatus() + self.sysinfo() + "getmode,0,end"
                print("sent:" + value)
                conn.sendall(value.encode())
                decoded_data = ""
            if decoded_data.endswith("shutdown,"):
                value = "shutdown,end"
                print("sent:" + value)
                conn.sendall(value.encode())
                AnycubicSimulator.shutdown_signal = True


def start_server(the_ip, port):
    """Starts the server"""
    AnycubicSimulator(the_ip, int(port)).start_server()


opts, args = getopt.gnu_getopt(sys.argv, "i:p:", [ "ipaddress=", "port="])

IP_ADDRESS = "0.0.0.0"
PORT = 6000
for opt, arg in opts:
    if opt in ("-i", "--ipaddress"):
        IP_ADDRESS = arg
    elif opt in ("-p", "--port"):
        PORT = arg
        print("Opening printer on port " + arg)



start_server(IP_ADDRESS, PORT)
