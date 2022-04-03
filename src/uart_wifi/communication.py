"""Communications with MonoX devices. -Adam Outler - email: adamoutler(a)hackedyour.info
The development environment is Visual Studio Code. See launch.json for auto-config.
"""


from asyncio.log import logger
from datetime import datetime
import os
import select
import sys
from queue import Empty

from socket import AF_INET, SOCK_STREAM, socket
import tempfile
from typing import Iterable

from uart_wifi.errors import ConnectionException

from .response import (
    FileList,
    InvalidResponse,
    MonoXPreviewImage,
    MonoXResponseType,
    MonoXStatus,
    MonoXSysInfo,
)


# Port to listen on

HOST = "192.168.1.254"
COMMAND = "getstatus"
endRequired = ["goprint", "gostop", "gopause", "delfile"]
END = ",end"
ENCODING = "gbk"
_LOGGER = logger
Any = object()
MAX_REQUEST_TIME = 10  # seconds
Response = Iterable[MonoXResponseType]


class UartWifi:  # pylint: disable=too-few-public-methods
    """Mono X Class"""

    def __init__(self, ip_address: str, port: int) -> None:
        """Create a communications UartWifi class.
        :ip_address: The IP to initiate communications with.
        :port: The port to use.
        """
        self.server_address = (ip_address, port)
        self.raw = False
        self.telnet_socket = socket(AF_INET, SOCK_STREAM)

    def send_request(self, message_to_be_sent: str) -> MonoXResponseType:
        """sends the Mono X request.
        :message_to_be_sent: The properly-formatted uart-wifi message as it is to be sent.
        :returns: an object from Response class.
        """
        request = bytes(message_to_be_sent, "utf-8")
        received: str = _do_request(self.telnet_socket, self.server_address, request)
        if self.raw:
            return received
        processed = _do_handle(received)
        return processed


def _do_request(
    sock: socket, socket_address: tuple, to_be_sent: bytes
) -> MonoXResponseType:
    """Perform the request

    :param sock: the socket to use for the request
    :param request: the request to send
    :return: a MonoX object"""
    text_received = ""
    try:
        sock = _setup_socket(socket_address)
        sock.sendall(to_be_sent)
        sent_string = to_be_sent.decode()
        if sent_string.endswith("shutdown"):
            return "shutdown,end"
        if sent_string.startswith("b'getPreview2"):
            text_received = bytearray()
            print(text_received)
            end_time = datetime.now().microsecond + 10000
            while (
                not str(text_received).endswith(END)
                and datetime.now().microsecond < end_time
            ):
                text_received.extend(sock.recv(1))
        else:
            text_received = ""
            read_list = [sock]
            port_read_delay = datetime.now().microsecond
            end_time = datetime.now().microsecond + 5000
            while True:
                current_time = datetime.now().microsecond
                if end_time > current_time or port_read_delay > current_time:
                    readable, [], [] = select.select(read_list, [], [])
                    for read_port in readable:
                        if read_port is sock:
                            port_read_delay = datetime.now().microsecond + 100
                            text_received += str(read_port.recv(1).decode())
                if text_received.endswith(",end"):
                    break

    except (OSError, ConnectionRefusedError, ConnectionResetError) as exception:
        raise ConnectionException(
            "Could not connect to AnyCubic printer at " + socket_address[0]
        ) from exception
    finally:
        sock.close()
    return text_received


def _setup_socket(socket_address):
    """Setup the socket for communication
    socket_address: the tupple consisting of (ip_address, port).
    """
    _LOGGER.debug("connecting to %s", socket_address)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(socket_address)
    sock.settimeout(MAX_REQUEST_TIME)
    return sock


def __do_preview2(received_message: bytearray()):
    """Handles preview by writing to file.
    :received_message: The message, as received from UART wifi protocol, to be converted to an image.
    """

    filename = received_message.decode("utf_8").split(",", 3)[1]
    file = tempfile.gettempdir() + os.path.sep + filename + ".bmp"
    print(file)

    output_file = open(file=file, mode="rb")

    width = 240
    height = 168

    file_size = os.path.getsize(file)
    pos_in_image = 0
    max_line_length = width * 2
    slices = []
    for row in range(0, height):
        current_slice = bytearray()
        for current_byte in range(0, max_line_length):
            current_byte = (row * max_line_length) + current_byte
            if file_size >= current_byte:
                current_slice.append(output_file.read(2))
            current_byte += 2
            slices.append(current_slice)

    my_slice = [[]]
    for byte in slices:
        print(type(byte))
        my_slice[pos_in_image] = byte[0]
        pos_in_image += 1
        if pos_in_image > (240 * 2):
            pos_in_image = 0
            current_slice = bytearray
            slices.append(current_slice)

    # image = Image.new("RGB", (width, height))
    # file_format = "bmp"  # The file extension of the sourced data
    print(len(slices))

    print(slice)

    # bytes(byte_array)
    # image.write(output_file,file_format)

    # output_file.close()

    return MonoXPreviewImage("")


def _do_handle(message: str) -> Iterable[MonoXResponseType]:
    """Perform handling of the message received by the request"""
    if message is None:
        return "no response"

    lines = message.split(",end")
    recognized_response: Iterable = list()
    for line in lines:
        fields: list(str) = line.split(",")
        message_type = fields[0]
        if len(fields) is Empty or len(fields) < 2:
            continue
        if message_type == "getstatus":
            recognized_response.append(__do_status(fields))
        elif message_type == "getfile":
            recognized_response.append(__do_files(fields))
        elif message_type == "sysinfo":
            recognized_response.append(__do_sys_info(fields))
        elif message_type == "gethistory":
            recognized_response.append(__do_get_history(fields))
        elif message_type == "doPreview2":
            recognized_response.append(__do_preview2(fields))
        # goprint,49.pwmb,end
        elif message_type in ["goprint", "gostop", "gopause", "getmode", "getwifi"]:
            recognized_response.append(InvalidResponse(fields[1]))
        else:
            print("unrecognized command: " + message_type, file=sys.stderr)
            print(line, file=sys.stderr)
            if recognized_response is not None:
                recognized_response.append(InvalidResponse(fields[1]))

    return recognized_response


def __do_get_history(fields: Iterable):
    """Handles history processing."""
    items = []
    for field in fields:
        if field in fields[0] or fields[-1]:
            continue
        items.append(field)
    return items


def __do_sys_info(fields: Iterable):
    """Handles system info processing."""
    sys_info = MonoXSysInfo()
    if len(fields) > 2:
        sys_info.model = fields[1]
    if len(fields) > 3:
        sys_info.firmware = fields[2]
    if len(fields) > 4:
        sys_info.serial = fields[3]
    if len(fields) > 5:
        sys_info.wifi = fields[4]
    return sys_info


def __do_files(fields: Iterable):
    """Handles file processing."""
    files = FileList(fields)
    return files


def __do_status(fields: Iterable):
    """Handles status processing."""
    status = MonoXStatus(fields)
    status.print()
    return status
