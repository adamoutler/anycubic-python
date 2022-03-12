"""Communications with MonoX devices. -Adam Outler - email: adamoutler(a)hackedyour.info
The development environment is Visual Studio Code. See launch.json for auto-config.
"""


from asyncio.log import logger
from datetime import datetime
import os
import sys
from queue import Empty
import socket
import tempfile

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
ENCODING = "utf-8"
_LOGGER = logger
Any = object()


class UartWifi:  # pylint: disable=too-few-public-methods
    """Mono X Class"""

    def __init__(self, ip_address: str, port: int) -> None:
        self.server_address = (ip_address, port)
        self.telnet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_request(self, message_to_be_sent: str) -> MonoXResponseType:
        """sends the Mono X request."""
        request: str = bytes(message_to_be_sent, "utf-8")
        received: str = _do_request(self.telnet_socket, self.server_address, request)
        processed: MonoXResponseType = _do_handle(received)
        return processed


def _do_request(
    sock: socket, socket_address: tuple, to_be_sent: bytes
) -> MonoXResponseType:
    """Perform the request

    :param sock: the socket to use for the request
    :param request: the request to send
    :return: a MonoX object"""

    try:
        _LOGGER.debug("connecting to %s", socket_address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(socket_address)
        sock.sendall(to_be_sent)
        if str(to_be_sent).startswith("b'getPreview2"):
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
            while not str(text_received).endswith(END):
                text_received += str(sock.recv(1).decode())
    except OSError as exception:
        _LOGGER.error(
            "Could not connect to AnyCubic printer at %s %s:%s",
            socket_address,
            exception.__class__,
            exception.__cause__,
        )
        return None
    finally:
        sock.close()
    return text_received


def __do_preview2(received_message: bytearray()):
    """Handles preview by writing to file."""

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


def _do_handle(message: Any):
    """Perform handling of the message received by the request"""
    if message is None:
        return "no response"

    lines = message.split("end")
    recognized_response: MonoXResponseType = None
    for line in lines:
        fields = line.split(",")
        message_type = fields[0]
        if len(fields) is Empty or len(fields) < 2:
            print("Done", file=sys.stderr)
            continue
        if len(fields) < 3:
            print(
                f"""Connection established, but no usable data was received.
            Transcript:\n{line}""",
                file=sys.stderr,
            )
            return ""
        if message_type == "getstatus":
            recognized_response = __do_status(fields)
        elif message_type == "getfile":
            recognized_response = __do_files(fields)
        elif message_type == "sysinfo":
            recognized_response = __do_sys_info(fields)
        elif message_type == "gethistory":
            recognized_response = __do_get_history(fields)
        elif message_type == "doPreview2":
            recognized_response = __do_preview2(fields)
        # goprint,49.pwmb,end
        elif message_type in ["goprint", "gostop", "gopause", "getmode", "getwifi"]:
            recognized_response = fields[1]
        else:
            print("unrecognized command: " + message_type, file=sys.stderr)
            print(line, file=sys.stderr)
        if recognized_response is not None:
            return recognized_response
        return InvalidResponse(line)


def __do_get_history(fields):
    """Handles history processing."""
    items = []
    for field in fields:
        if field in fields[0] or fields[-1]:
            continue
        items.append(field)
    return items


def __do_sys_info(fields):
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


def __do_files(fields):
    """Handles file processing."""
    files = FileList(fields)
    return files


def __do_status(fields):
    """Handles status processing."""
    status = MonoXStatus(fields)
    return status
