import getopt
import socket
import sys


class AnycubicSimulator:
    """ "Simulator for Anycubic Printer."""

    ip_address = "127.0.0.1"
    port = "6000"
    printing = False
    serial = "0000170300020034"

    def __init__(self, ip_address: str, port: int) -> None:
        self.host = ip_address
        self.port = port
        self.printing = False
        self.serial = "234234234"

    def sysinfo(self) -> str:
        """return sysinfo type"""
        return (
            "sysinfo,Photon Mono X 6K,V0.2.2,"
            + self.serial
            + ",SkyNet,endgetstatus,stop"
        )

    def getfile(self) -> str:
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
        """Do printing"""
        if not self.printing:
            return "gostop,ERROR1,end"
        self.printing = False
        return "gostop,OK,end"
    def getmode(self) -> str:
        """return getmode type"""
        return "getmode,0,end"

    def start_server(self):
        """Start the uart_wifi simualtor server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.ip_address, self.port))
                s.listen()
                conn, addr = s.accept()
                data_received = ""
                with conn:
                    print(f"Connected by {addr}")
                    while True:

                        data = conn.recv(1024)
                        if not data:
                            break
                        try:
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
                                conn.sendall(self.getmode().encode())
                            data_received = ""
            finally:
                s.close()


opts, args = getopt.gnu_getopt(sys.argv, "i:p:", ["ipaddress=", "port="])

ip = "0.0.0.0"
port = 6000
for opt, arg in opts:
    if opt in ("-i", "--ipaddress"):
        ip = arg
    elif opt in ("-p", "--port"):
        port = arg
        print(arg)
AnycubicSimulator(ip, int(port)).start_server()
