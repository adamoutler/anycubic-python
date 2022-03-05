"""Communications with MonoX devices. -Adam Outler - email: adamoutler(a)hackedyour.info
The development environment is Visual Studio Code. See launch.json for auto-config.
"""
from queue import Empty
import socket
import sys
import getopt



PORT = 6000  # Port to listen on

HOST = "192.168.1.254"
COMMAND = 'getstatus'
endRequired = ["goprint", "gostop", "gopause", "delfile"]

HELP = __file__ + \
    """
monox.py | Adam Outler (monox@hackedyour.info) | GPLv3

Usage: monox.py -i <ip address> -c <command>
args:
 -i [--ipaddress=] - The IP address which your Anycubic Mono X can be reached

 -c [--command=] - The command to send.
   Commands may be used one-at-a-time. Only one command may be sent and it is
        expected to be in the format below.
    Command: getstatus - Returns a list of printer statuses.
    Command: getfile - returns a list of files in format
        <internal name>: <file name>. When referring to the
        file via command, use the <internal name>.
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

try:
    opts, args = getopt.gnu_getopt(
        sys.argv, "hi:c:", ["ipaddress=", "command="])
# pylint: disable=broad-except
except Exception:
    print(HELP)
    sys.exit(0)

for opt, arg in opts:
    if opt == '-h':
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


def __do_request(sock, server_to_connect, request_string):
    """Perform the request"""
    received_message = ""
    try:
        print(f"connecting to {server_to_connect} port {PORT}", file=sys.stderr)
        sock.connect(server_to_connect)
        sock.sendall(request_string)
        while not str(received_message).endswith('end'):
            received_message += str(sock.recv(1).decode())
    finally:
        sock.close()
    return received_message


def __do_handle(message):
    """Perform handling of the message received by the request"""
    lines = message.split("end")
    recognized_response:MonoXResponseType=None
    for line in lines:
        fields = line.split(",")
        message_type = fields[0]
        if len(fields) is Empty or len(fields) < 2:
            print('Done', file=sys.stderr)
            continue
        if len(fields) < 3:
            print(f'''Connection established, but no usable data was received.
            Transcript:\n{line}''', file=sys.stderr)
            return ""
        if message_type == "getstatus":
            recognized_response= __do_status(fields)
        if message_type == "getfile":
            recognized_response= __do_files(fields)
        if message_type == "sysinfo":
            recognized_response= __do_sys_info(fields)
        if message_type == 'gethistory':
            recognized_response= __do_get_history(fields)
        # goprint,49.pwmb,end
        if message_type in ["goprint" , "gostop" , "gopause" , "getmode" , "getwifi"]:
            recognized_response= fields[1]

        print("unrecognized command: "+message_type, file=sys.stderr)
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
    status = MonoXStatus()
    if len(fields) > 2:
        status = MonoXStatus(fields[1])
    if len(fields) > 3:
        status = MonoXStatus(fields[1], fields[2])
    if len(fields) > 4:
        status = MonoXStatus(fields[1], fields[2], fields[3])
    if len(fields) > 13:
        status = MonoXStatus(fields[1], fields[2], fields[3], fields[4], fields[5],
                             fields[6], fields[7], fields[8], fields[9], fields[10],
                             fields[11], fields[12])
    return status

##pylint: disable=too-few-public-methods
class MonoXResponseType:
    """The baseline MonoX State class"""

    status: str = "error/offline"
    def print(self):
        """Print the MonoXResponse. Should be overridden by anything which implements this class."""
        return "Status: "+str



class MonoXFileEntry(MonoXResponseType):
    """A file entry consisting of an internal and external listing"""

    def __init__(self, internal_name: str, external_name: str):
        self.external = internal_name
        self.internal = external_name
        self.status = "file"

    def print(self):
        print(self.internal+": "+self.external)


class FileList(MonoXResponseType):
    """handles lists of files"""

    files = [MonoXFileEntry]

    def __init__(self, data: MonoXFileEntry):
        self.files = []
        self.status = "getfile"

        for field in data:
            if field in data[0] or data[-1]:
                continue  # not interested in packet open/close portion.
            split = field.split("/")
            self.files.append(MonoXFileEntry(split[0], split[1]))

    def print(self):
        for file in self.files:
            file.print()


class InvalidResponse(MonoXResponseType):
    """Used when no response is provided"""

    def __init__(self, message):
        self.status = message

    def print(self):
        print("Invalid Response: "+self.status)


class MonoXSysInfo(MonoXResponseType):
    """The sysinfo handler. Handles sysinfo messages.

    eg message.
        sysinfo
        sysinfo,Photon Mono X 6K,V0.2.2,0000170300020034,SkyNet,end
    """

    model: str
    firmware: str
    serial: str
    wifi: str

    def __init__(self, model="", firmware="", serial="", wifi=""):
        self.model = model
        self.firmware = firmware
        self.serial = serial
        self.wifi = wifi
        self.status = "updated"

    def print(self):
        print("model: "+self.model)
        print("firmware: "+self.firmware)
        print("serial: "+self.serial)
        print("wifi: "+self.wifi)


class MonoXStatus(MonoXResponseType):
    """Status object for MonoX.

    eg message.
        getstatus
        getstatus,stop
    """

    def __init__(
        self,
        status="",
        file="none",
        total_layers=0,
        layers_remaining=0,
        current_layer=0,
        seconds_elapse=0,
        seconds_remaining=0,
        total_volume=0,
        mode="UV",
        unknown1=0,
        layer_height=0,
        unknown2=0,
    ):

        self.status = status
        self.file = file
        self.total_layers = total_layers
        self.layers_remaining = layers_remaining
        self.current_layer = current_layer
        self.seconds_elapse = seconds_elapse
        self.seconds_remaining = seconds_remaining
        self.total_volume = total_volume
        self.mode = mode
        self.unknown1 = unknown1
        self.layer_height = layer_height
        self.unknown2 = unknown2

    def print(self):
        print("status: "+self.status)
        print("file: "+self.file)
        print("total_layers: "+str(self.total_layers))
        print("layers_remaining: "+str(self.layers_remaining))
        print("current_layer: "+str(self.current_layer))
        print("seconds_remaining: "+str(self.seconds_remaining))
        print("total_volume: "+str(self.total_volume))
        print("mode: "+self.mode)
        print("unknown1: "+str(self.unknown1))
        print("layer_height: "+str(self.layer_height))
        print("unknown2: "+str(self.unknown2))


request: str = bytes(COMMAND, "utf-8")
received: str = __do_request(telnet_socket, server_address, request)

processed = __do_handle(received)
if isinstance(processed, MonoXResponseType):
    processed.print()
elif isinstance(processed, dict):
    for k, v in processed.items():
        if v == str:
            continue
        print(k+": "+v)
elif isinstance(processed, list):
    for item in processed:
        if isinstance(item, dict):
            for k, v in item.items():
                print(v+": "+k)
        else:
            print(item)
else:
    print(processed)
