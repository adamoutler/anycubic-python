A script to gather information from the Mono X printer.  This is tested working on the Anycubic Mono X 6k and should work on any Mono X or Mono SE printer. 

    Usage: monox.py -i <ip address> -c <command>
    args:
     -i [--ipaddress=] - The IP address which your Anycubic Mono X can be reached

     -c [--command=] - The command to send.
    
    Commands may be used one-at-a-time. Only one command may be sent and it is expected to be in the format below.

    Command: getstatus - Returns a list of printer statuses.
   
    Command: getfile - returns a list of files in format <internal name>: <file name>.  When referring to the file via command, use the <internal name>.
    
    Command: sysinfo - returns Model, Firmware version, Serial Number, and wifi network.
    
    Command: getwifi - displays the current wifi network name.
    
    Command: gopause - pauses the current print.
    
    Command: goresume - ends the current print.
    
    Command: gostop,end - stops the current print.
    
    Command: delfile,<internal name>,end - deletes a file.
    
    Command: gethistory,end - gets the history and print settings 
    of previous prints.
    
    Command: delhistory,end - deletes printing history.
    
    Command: goprint,<internal name>,end - Starts a print of the 
    requested file
    
    Command: getPreview1,<internal name>,end - returns a list of dimensions used for the print.
