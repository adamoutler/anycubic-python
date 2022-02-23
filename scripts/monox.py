import asyncio
from queue import Empty
import socket
import sys
import getopt
import collections
from tkinter import FIRST, LAST


PORT = 6000  # Port to listen on

host = "192.168.1.254"
command = 'getstatus'
endRequired=["goprint","gostop","gopause","delfile"]

help = __file__ + \
    """
monox.py | Adam Outler (monox@hackedyour.info) | GPLv3

Usage: monox.py -i <ip address> -c <command>
args:
 -i [--ipaddress=] - The IP address which your Anycubic Mono X can be reached\n 
 -c [--command=] - The command to send.
   Commands may be used one-at-a-time. Only one command may be sent and it is expected to be in the format below. 
    Command: getstatus - Returns a list of printer statuses.
    Command: getfile - returns a list of files in format <internal name>: <file name>. When referring to the file via command, use the <internal name>. 
    Command: getwifi - displays the current wifi network name.
    Command: gopause,end - pauses the current print.
    Command: goresume,end - ends the current print.
    Command: gostop,end - stops the current print.
    Command: delfile,<internal name>,end - deletes a file.
    command: gethistory,end - gets the history and print settings of previous prints. 
    Command: delhistory,end - deletes printing history.
    Command: goprint,<internal name>,end - Starts a print of the requested file
    Command: getPreview1,<internal name>,end - returns a list of dimensions used for the print.

   Not Supported Commands may return unusable results.    
    Command (Not Supported): getPreview2,<internal name>,end - returns a binary preview image of the print.

   Unknown Commands are at your own risk and experimentation. No attempt is made to process or stop execution of these commands.
    Command: detect
    Command: stopUV - unknown
    Command: getpara - unknown
    Command: getmode - unknown
    Command: setname - unknown
    Command: setwifi - unknown
    Command: setZero - unknown
    Command: setZhome - unknown
    Command: setZmove - unknown
    Command: setZstop - unknown
    """

try:
    opts, args = getopt.gnu_getopt(sys.argv, "hi:c:", ["ipaddress=", "command="])
except:
    print(help)
    sys.exit()

for opt, arg in opts:
    if opt == '-h':
        print(help)
        sys.exit()
    elif opt in ("-i", "--ipaddress"):
        host = arg
    elif opt in ("-c", "--command"):
        command = arg
        print (arg)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port on the server given by the caller
server_address = (host, PORT)


def doRequest(sock, server_address, request):
    received = ""
    try:
        print('connecting to %s port %s' % server_address, file=sys.stderr)
        sock.connect(server_address)
        sock.sendall(request)
        while not str(received).endswith('end'):
            received += str(sock.recv(1).decode())
    finally:
        sock.close()
        return received

def doHandle(message):
    lines = message.split("end")
    for line in lines:
        fields = line.split(",")
        type = fields[0]
        if (len(fields) is Empty or len(fields)<2):
            print('Done', file=sys.stderr)
            return ""
        if (len(fields)<3):
            print('Connection established, but no usable data was received. Transcript:\n%s' % line, file=sys.stderr)
            return ""
        if type == "getstatus":
            return doStatus(fields)
        if (type== "getfile"):
            return doFiles(fields)
        if (type=="sysinfo"):
            return doSysInfo(fields)
        if (type=='gethistory'):
            return doGetHistory(fields)
        #goprint,49.pwmb,end
        if (type=="goprint") or (type=="gostop") or (type=="gopause") or (type=="getmode") or (type=="getwifi"):
            return fields[1]
        else:
            print("unrecognized command: "+type, file=sys.stderr)
            print(line, file=sys.stderr)


def doGetHistory(fields): 
    items=[]
    for field in fields:
        if field == fields[0] or field==fields[-1]:
            continue
        items.append(field)
    return items
     
def doSysInfo(fields):
    status =  {"model":str,"firmware":str, "serial":str, "wifi":str}
    if (len(fields) > 2):
        status["model"]=fields[1]
    if (len(fields) > 3):
        status["firmware"]=fields[2]
    if (len(fields) > 4):
        status["serial"]=fields[3]
    if (len(fields) > 5):
        status["wifi"]=fields[4]
    return status


            
def doFiles(fields):
    files=[]
    for field in fields:
        if field == fields[0] or field==fields[-1]:
            continue
        split=field.split("/")
        files.append({split[0]:split[1]})
    return files
    

def doStatus(fields):
    status =  {"status":str,"file":str,"total_layers":str,"layers_remaining":str,"current_layer":str,"seconds_elapse":str,"seconds_remaining":str,"total_volume":str,"mode":str,"unknown1":str,"layer_height":str,"unknown2":str}
    if (len(fields) > 2):
        status["status"]=fields[1]
    if (len(fields) > 3):
        status["file"]=fields[2]
    if (len(fields) > 4):
        status["total_layers"]=fields[3]
    if (len(fields) > 5):
        status["layers_remaining"]=fields[4]
    if (len(fields) > 6):
        status["current_layer"]=fields[5]
    if (len(fields) > 7):
        status["seconds_elapsed"]=fields[6]
    if (len(fields) > 8):
        status["seconds_remaining"]=fields[7]
    if (len(fields) > 9):
        status["total_volume"]=fields[8]
    if (len(fields) > 10):
        status["mode"]=fields[9]
    if (len(fields) > 11):
        status["unknown1"]=fields[10]
    if (len(fields) > 12):
        status["layer_height"]=fields[11]
    if (len(fields) > 13):
        status["unknown2"]=fields[12]
    return status


request = bytes(command, "utf-8")
received = doRequest(sock, server_address, request)

processed=doHandle(received)
if (type(processed) is dict ):
    for k, v in processed.items():
        if v == str:
             continue
        print(k+": "+v)
elif (type(processed) is list):
    for item in processed:
        if item is dict:
           for k, v in item.items():
               print(v+": "+k)       
        else:
            print(item)
else: 
    print(processed)    

