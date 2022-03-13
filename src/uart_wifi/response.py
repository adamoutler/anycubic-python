"""Mono X Objects"""

##pylint: disable=too-few-public-methods
class MonoXResponseType:
    """The baseline MonoX State class"""

    status: str = "error/offline"

    def print(self):
        """Print the MonoXResponse. Should be overridden by anything which implements this class."""
        return "Status: " + self.status


class MonoXFileEntry(MonoXResponseType):
    """A file entry consisting of an internal and external listing"""

    def __init__(self, internal_name: str, external_name: str) -> None:
        self.external = internal_name
        self.internal = external_name
        self.status = "file"

    def print(self):
        print(self.internal + ": " + self.external)


class FileList(MonoXResponseType):
    """handles lists of files"""

    def __init__(self, data: MonoXFileEntry) -> None:
        self.files = []
        self.status = "getfile"

        for field in data:
            if field in data[0] or data[-1]:
                continue  # not interested in packet open/close portion.
            split = field.split("/")
            self.files.append(MonoXFileEntry(split[0], split[1]))

    files = [MonoXFileEntry]

    def print(self):
        for file in self.files:
            file.print()


class InvalidResponse(MonoXResponseType):
    """Used when no response is provided"""

    def __init__(self, message) -> None:
        self.status = message

    def print(self):
        print("Invalid Response: " + self.status)


class SimpleResponse(MonoXResponseType):
    """Used when no response is provided"""

    def __init__(self, message) -> None:
        self.status = message

    def print(self):
        print("Response: " + self.status)


class MonoXSysInfo(MonoXResponseType):
    """The sysinfo handler. Handles sysinfo messages.

    eg message.
        sysinfo
        sysinfo,Photon Mono X 6K,V0.2.2,0000170300020034,SkyNet,end
    """

    def __init__(self, model="", firmware="", serial="", wifi="") -> None:
        self.model = model
        self.firmware = firmware
        self.serial = serial
        self.wifi = wifi
        self.status = "updated"

    def print(self):
        print("model: " + self.model)
        print("firmware: " + self.firmware)
        print("serial: " + self.serial)
        print("wifi: " + self.wifi)


class MonoXStatus(MonoXResponseType): #pylint: disable=too-many-instance-attributes
    """Status object for MonoX.

    eg message.
        getstatus
        getstatus,stop
    """
    def __init__(self, message) -> None:

        self.status = message[1]
        if len(message) > 3:
            self.file = message[2]
            self.total_layers = message[3]
            self.layers_remaining = message[4]
            self.current_layer = message[5]
            self.seconds_elapse = message[6]
            self.seconds_remaining = message[7]
            self.total_volume = message[8]
            self.mode = message[9]
            self.unknown1 = message[10]
            self.layer_height = message[11]
            self.unknown2 = message[12]

    def print(self):
        print("status: " + self.status)
        if hasattr(self, "file"):
            print("file: " + self.file)
            print("total_layers: " + str(self.total_layers))
            print("layers_remaining: " + str(self.layers_remaining))
            print("current_layer: " + str(self.current_layer))
            print("seconds_remaining: " + str(self.seconds_remaining))
            print("total_volume: " + str(self.total_volume))
            print("mode: " + self.mode)
            print("unknown1: " + str(self.unknown1))
            print("layer_height: " + str(self.layer_height))
            print("unknown2: " + str(self.unknown2))


class MonoXPreviewImage(MonoXResponseType):
    """A file entry consisting of an internal and external listing"""

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path
        self.status = "preview image"

    def print(self):
        print(f"preview located at {self.file_path}")
