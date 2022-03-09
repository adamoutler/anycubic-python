"""Handles communication and processing of Monox.

This is used for receiving status updates, and sending print, pause, stop commands.

This is a telnet protocol. Status request commands are EOM or \n terminated. Action requests (such as print, stop pause and move)
are ",end\n" terminated. Parameters are comma delmeted.  Commands which require parameters are sent as "goprint,30.pwmb,end\n"
whereas a simple status request may be accomplished via "getstatus\n".

The protocol was reverse engineered via official Android App and is incomplete in that most dangersous commands are not supported.

A complete list of applicable devices are found within the app as follows:
SLA: "Photon Mono SE", "Photon Mono X", "Photon X", "Photon Mono X 6K"
FDM: "Mega", "Mega S", "Mega X", "Mega Zero", "Mega Pro", "Chiron", "Predator"
"""
from queue import Empty
from .monoxresponse import (
    MonoXSysInfo,
    MonoXResponseType,
    MonoXStatus,
    FileList,
)
import logging
import socket

from config.custom_components.anycubic_uart import monoxresponse

_LOGGER = logging.getLogger(__name__)

MONOXPORT = 6000

GETSTATUS_COMMAND = "getstatus"  # stop, pause, finish, or print + MonoXStatus
GETFILES_COMMAND = (
    "getfile"  # list of files/internal names https://hackedyour.info/8BUsO0qnKPZ9gWvx
)
SYSINFO_COMMAND = (
    "sysinfo"  # System and wifi info https://hackedyour.info/ZvIS5Vk5s9rUJqnw
)
GETHISTORY_COMMAND = "gethistory"  # status for each recently printed item https://hackedyour.info/KnVG9LEjf8PBXmm8
GOPRINT_COMMAND = "goprint"  # ok, or error, goprint,30.pwmb,end
GOSTOP_COMMAND = "gostop"  # ok, or error, gostop,end
GOPAUSE_COMMAND = "gopause"  # ok, or error gopause,end
GETMODE_COMMAND = "getmode"  # mode number 0 - unknown modes
GETWIFI_COMMAND = "getwifi"  # name of wifi network
END = ",end"
ENCODING = "utf-8"


class MonoX:
    """Communication with Mono X printer"""

    def __init__(self, ip_address):  # instance-dependent method
        """initialize the MonoX object with an IP address required for comms."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip_address, 6000)

    PORT = 6000  # Port to listen on

    def get_status(self) -> MonoXStatus:
        """Get the status"""
        response = self.do_request(self.sock, bytes(GETSTATUS_COMMAND, ENCODING))
        status = MonoX.do_handle(response)
        if isinstance(status, monoxresponse.MonoXStatus):
            return status
        return None

    def get_sysinfo(self) -> MonoXSysInfo:
        """Get the status"""
        response = self.do_request(self.sock, bytes(SYSINFO_COMMAND, ENCODING))
        status = MonoX.do_handle(response)
        if isinstance(status, monoxresponse.MonoXSysInfo):
            return status
        return None

    def do_request(self, sock, request) -> MonoXResponseType:
        """Perform the request

        :param sock: the socket to use for the request
        :param request: the request to send
        :return: a MonoX object"""
        received = ""
        try:
            _LOGGER.debug("connecting to %s", self.server_address)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server_address)
            sock.sendall(request)
            while not str(received).endswith(END):
                received += str(sock.recv(1).decode())
        except OSError as exception:
            _LOGGER.error(
                "Could not connect to AnyCubic printer at %s %s:%s",
                self.server_address,
                exception.__class__,
                exception.__cause__,
            )
            return None
        finally:
            sock.close()
        return received

    @staticmethod
    def do_get_history(fields):
        """Handles gethistory messages from the unit"""
        items = []
        for field in fields:
            if field in fields[0] or fields[-1]:
                continue
            items.append(field)
        return monoxresponse.InvalidResponse(items)

    @staticmethod
    def do_sys_info(fields) -> MonoXSysInfo:
        """Handles sysinfo messages from the unit"""
        status = MonoXSysInfo()
        if len(fields) > 2:
            status.model = fields[1]
        if len(fields) > 3:
            status.firmware = fields[2]
        if len(fields) > 4:
            status.serial = fields[3]
        if len(fields) > 5:
            status.wifi = fields[4]
        return status

    @staticmethod
    def do_files(fields) -> FileList:
        """Handles getFiles messages from the unit"""
        files = FileList(fields)
        return files

    @staticmethod
    def do_status(fields) -> MonoXStatus:
        """Handles getstatus messages from the unit"""
        message = MonoXStatus()
        if len(fields) > 2:
            message.status = fields[1]
        if len(fields) > 3:
            message.file = fields[2]
        if len(fields) > 4:
            message.total_layers = fields[3]
        if len(fields) > 5:
            message.layers_remaining = fields[4]
        if len(fields) > 6:
            message.current_layer = fields[5]
        if len(fields) > 7:
            message.seconds_elapse = fields[6]
        if len(fields) > 8:
            message.seconds_remaining = fields[7]
        if len(fields) > 9:
            message.total_volume = fields[8]
        if len(fields) > 10:
            message.mode = fields[9]
        if len(fields) > 11:
            message.unknown1 = fields[10]
        if len(fields) > 12:
            message.layer_height = fields[11]
        if len(fields) > 13:
            message.unknown2 = fields[12]
        return message

    @staticmethod
    def do_handle(message) -> MonoXResponseType:
        """Handles messages from the unit"""
        lines = message.split("end")
        for line in lines:
            fields = line.split(",")
            message_type = fields[0]
            if len(fields) is Empty or len(fields) < 2:
                _LOGGER.debug("Request Done")
                return ""
            if len(fields) < 3:
                _LOGGER.debug(
                    "Connection established, but no usable data was received. Transcript:\n%s",
                    line,
                )
                return ""
            if message_type == GETSTATUS_COMMAND:
                return MonoX.do_status(fields)
            if message_type == GETFILES_COMMAND:
                return MonoX.do_files(fields)
            if message_type == SYSINFO_COMMAND:
                return MonoX.do_sys_info(fields)
            if message_type == GETHISTORY_COMMAND:
                return MonoX.do_get_history(fields)
            # goprint,49.pwmb,end
            if message_type in [
                GOPRINT_COMMAND,
                GOSTOP_COMMAND,
                GOPAUSE_COMMAND,
                GETMODE_COMMAND,
                GETWIFI_COMMAND,
            ]:
                return monoxresponse.SimpleResponse(fields[1])
            else:
                _LOGGER.error("unrecognized command: " + message_type + "\n" + line)
                return monoxresponse.InvalidResponse(fields)
