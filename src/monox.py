"""Communications with MonoX devices. -Adam Outler - email: adamoutler(a)hackedyour.info
The development environment is Visual Studio Code. See launch.json for auto-config.
"""


from asyncio.log import logger
from datetime import datetime
import os
import sys
from queue import Empty
import socket
import getopt
import tempfile


from monox_response import (
    FileList,
    InvalidResponse,
    MonoXPreviewImage,
    MonoXResponseType,
    MonoXStatus,
    MonoXSysInfo,
)


PORT = 6000  # Port to listen on

HOST = "192.168.1.254"
COMMAND = "getstatus"
endRequired = ["goprint", "gostop", "gopause", "delfile"]
END = ",end"
ENCODING = "utf-8"
_LOGGER = logger

HELP = (
    __file__
    + """
monox.py | Adam Outler (monox@hackedyour.info) | GPLv3

Usage: monox.py -i <ip address> -c <command>
args:
 -i [--ipaddress=] - The IP address which your Anycubic Mono X can be reached

 -c [--command=] - The command to send.
   Commands may be used one-at-a-time. Only one command may be sent and it is
        expected to be in the format below.
    Command: getstatus - Returns a list of printer statuses.
    Command: getfile - returns a list of files in format <internal name>: <file name>.
        When referring to the file via command, use the <internal name>.
    Command: sysinfo - returns Model, Firmware version, Serial Number, and wifi network.
    Command: getwifi - displays the current wifi network name.
    Command: gopause - pauses the current print.
    Command: goresume - ends the current print.
    Command: gostop,end - stops the current print.
    Command: delfile,<internal name>,end - deletes a file.
    command: gethistory,end - gets the history and print settings of previous prints.
    Command: delhistory,end - deletes printing history.
    Command: goprint,<internal name>,end - Starts a print of the requested file
    Command: getPreview1,<internal name>,end - returns a list of dimensions used for the print.

   Not Supported Commands may return unusable results.
    Command (Not Supported): getPreview2,<internal name>,end
     - returns a binary preview image of the print.

   Unknown Commands are at your own risk and experimentation.
   No attempt is made to process or stop execution of these commands.
    Command: detect
    Command: stopUV - unknown
    Command: getpara - unknown
    Command: getmode - unknown
    Command: setname - unknown
    Command: getname - unknown
    Command: setwifi - unknown
    Command: setZero - unknown
    Command: setZhome - unknown
    Command: setZmove - unknown
    Command: setZstop - unknown
    """
)

try:
    opts, args = getopt.gnu_getopt(sys.argv, "hi:c:", ["ipaddress=", "command="])
# pylint: disable=broad-except
except Exception:
    print(HELP)
    sys.exit(0)

for opt, arg in opts:
    if opt == "-h":
        print(HELP)
        sys.exit()
    elif opt in ("-i", "--ipaddress"):
        HOST = arg
    elif opt in ("-c", "--command"):
        COMMAND = arg
        print(arg)

# Create a TCP/IP socket
telnet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port on the server given by the caller
server_address = (HOST, PORT)


def __do_request(sock, socket_address, to_be_sent) -> MonoXResponseType:
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


def __do_preview2(received_message):
    """Handles preview by writing to file."""
    tempdir = tempfile.gettempdir()
    filename = received_message.decode("utf_8").split(",", 3)[1]
    file = tempdir + os.path.sep + filename + ".bmp"
    print(file)

    # output_file = open(file=file, mode="wb")
    # byte_array = bytearray()
    # so    ck.setblocking(0)
    # ready = select.select([sock], [], [], 15)
    # try:
    #     while ready:
    #         byte_array.append(sock.recv(1)[0])
    # except BlockingIOError:
    #     sock.close()
    # finally:
    #     sock.close()

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


def __do_handle(message):
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
        if field == fields[0] or field == fields[-1]:
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


request: str = bytes(COMMAND, "utf-8")
received: str = __do_request(telnet_socket, server_address, request)

processed = __do_handle(received)
if isinstance(processed, MonoXResponseType):
    processed.print()
elif isinstance(processed, dict):
    for k, v in processed.items():
        if v == str:
            continue
        print(k + ": " + v)
elif isinstance(processed, list):
    for item in processed:
        if isinstance(item, dict):
            for k, v in item.items():
                print(v + ": " + k)
        else:
            print(item)
else:
    print(processed)
