"""Mono X Objects"""

##pylint: disable=too-few-public-methods
class MonoXResponseType:
    """The baseline MonoX State class"""

    status: str = "error/offline"

    def print(self):
        """Print the MonoXResponse. Should be overridden by anything which implements this class."""
        return "Status: " + str


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

    model: str
    firmware: str
    serial: str
    wifi: str

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
    ) -> None:

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
        print("status: " + self.status)
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
