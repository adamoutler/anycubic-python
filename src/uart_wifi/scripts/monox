#! python3
"""Uart wifi"""

import getopt
import sys
import time
from typing import Iterable

from uart_wifi.communication import UartWifi
from uart_wifi.errors import ConnectionException
from uart_wifi.response import MonoXResponseType


PORT = 6000
HELP = (
    __file__
    + """ | Adam Outler (monox@hackedyour.info) | GPLv3

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
    opts, args = getopt.gnu_getopt(
        sys.argv, "drhi:c:p:", ["raw", "ipaddress=", "command=", "port="]
    )
# pylint: disable=broad-except
except Exception as e:
    print(HELP)
    sys.exit(0)

USE_RAW = False
for opt, arg in opts:
    if opt == "-h":
        print(HELP)
        sys.exit()
    elif opt in "-d":
        time.sleep(1)
    elif opt in ("-r", "--raw"):
        USE_RAW = True
    elif opt in ("-i", "--ipaddress"):
        ip_address = arg
    elif opt in ("-p", "--port"):
        PORT = int(arg)
    elif opt in ("-c", "--command"):
        command = arg
        print(arg)

if "ip_address" not in locals():
    print("You must specify the host ip address (-i xxx.xxx.xxx.xxx)")
    sys.exit(1)

if ip_address == "127.0.0.1":
    time.sleep(1)
Responses = None
# Try 3 times to get the data.
attempts: int = 0
while attempts < 3:
    try:
        uart = UartWifi(ip_address, PORT)
        if USE_RAW:
            uart.raw = True
        Responses: Iterable[MonoXResponseType] = uart.send_request(command)
        break
    except ConnectionException:
        attempts += 1


if Responses != None and isinstance(Responses, list):
    for response in Responses:
        if isinstance(response, MonoXResponseType):
            response.print()
        else:
            print(response)
else:
    print(Responses)
