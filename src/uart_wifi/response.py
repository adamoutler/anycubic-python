"""Mono X Objects."""

##pylint: disable=too-few-public-methods
class MonoXResponseType:
    """The baseline MonoX Response class.  Use this to create other MonoX Responses."""

    status: str = "error/offline"

    def print(self):
        """Print the MonoXResponse. Should be overridden by anything which implements this class."""
        return "Status: " + self.status


class MonoXFileEntry(MonoXResponseType):
    """A file entry consisting of an internal and external listing"""

    def __init__(self, internal_name: str, external_name: str) -> None:
        """Create a MonoXFileEntry
        :internal_name: the name the printer calls the file. eg "1.pwmb"
        :external_name: The name the user calls the file. eg "My (Super) Cool.pwmb"
        """
        self.external = internal_name
        self.internal = external_name
        self.status = "file"

    def print(self):
        """Provide a human-readable response"""
        print(self.internal + ": " + self.external)


class FileList(MonoXResponseType):
    """handles lists of files.
    eg.
    getfile,
    2-phone-stands.pwmb/0.pwmb,
    SLA print puller supported.pwmb/1.pwmb,
    2 phone stands on side.pwmb/2.pwmb,
    5x USB_Cable_Holder_7w_Screws_hollow.pwmb/3.pwmb,
    end
    """

    def __init__(self, data: MonoXFileEntry) -> None:
        """Create a FileList object.
        :data: a list of internal/external files.
        """
        self.files = []
        self.status = "getfile"

        for field in data:
            if field in data[0] or data[-1]:
                continue  # not interested in packet open/close portion.
            split = field.split("/")
            self.files.append(MonoXFileEntry(split[0], split[1]))

    files = [MonoXFileEntry]

    def print(self):
        """Provide a human-readable response."""
        for file in self.files:
            file.print()


class InvalidResponse(MonoXResponseType):
    """Used when no response is provided."""

    def __init__(self, message) -> None:
        """Construct the InvalidResponse type.
        :message: anything goes
        """
        self.status = message

    def print(self):
        """Provide a human-readable response."""
        print("Invalid Response: " + self.status)


class SimpleResponse(MonoXResponseType):
    """Used when no response is provided."""

    def __init__(self, message) -> None:
        """Construct a SimpleResponse.
        :message: anything goes."""
        self.status = message

    def print(self):
        """Provide a human-readable response."""
        print("Response: " + self.status)


class MonoXSysInfo(MonoXResponseType):
    """The sysinfo handler. Handles sysinfo messages.
    eg message.
        sysinfo,Photon Mono X 6K,V0.2.2,0000170300020034,SkyNet,end
    """

    def __init__(self, model="", firmware="", serial="", wifi="") -> None:
        """Construct the MonoXSysInfo response type"""
        self.model = model
        self.firmware = firmware
        self.serial = serial
        self.wifi = wifi
        self.status = "updated"

    def print(self):
        """Provide a human-readable response"""
        print("model: " + self.model)
        print("firmware: " + self.firmware)
        print("serial: " + self.serial)
        print("wifi: " + self.wifi)


class MonoXStatus(MonoXResponseType):  # pylint: disable=too-many-instance-attributes
    """Status object for MonoX.

    eg message.
       getstatus,print,Widget.pwmb/46.pwmb,2338,88,2062,51744,6844,~178mL,UV,39.38,0.05,0,end
    """

    def __init__(self, message) -> None:
        """Construct the Status response.
        :message: a properly formated message of either length 3 or >12."""

        self.status = message[1]
        if len(message) > 2:
            self.file = message[2]
        if len(message) > 3:
            self.total_layers = message[3]
        if len(message) > 4:
            self.unknown = message[4]
        if len(message) > 5:
            self.current_layer = message[5]
        if len(message) > 6:
            if str(message[6]).isnumeric():
                self.seconds_elapse = int(message[6]) * 60
            else:
                self.seconds_elapse = message[6]
        if len(message) > 7:
            self.seconds_remaining = message[7]
        if len(message) > 8:
            self.total_volume = message[8]
        if len(message) > 9:
            self.mode = message[9]
        if len(message) > 10:
            self.unknown1 = message[10]
        if len(message) > 11:
            self.layer_height = message[11]
        if len(message) > 12:
            self.unknown2 = message[12]

    def print(self):
        """Provide a human-readable response."""
        print("status: " + self.status)
        if hasattr(self, "file"):
            print("file: " + self.file)
            print("total_layers: " + str(self.total_layers))
            print("unknown: " + str(self.unknown))
            print("current_layer: " + str(self.current_layer))
            print("seconds_remaining: " + str(self.seconds_remaining))
            print("total_volume: " + str(self.total_volume))
            print("mode: " + self.mode)
            print("unknown1: " + str(self.unknown1))
            print("layer_height: " + str(self.layer_height))
            print("unknown2: " + str(self.unknown2))


class MonoXPreviewImage(MonoXResponseType):
    """A file entry consisting of an internal and external listing."""

    def __init__(self, file_path: str) -> None:
        """Construct the MonoXPreviewImage.
        :file_path: the path to the preview image.
        """
        super().__init__()
        self.file_path = file_path
        self.status = "preview image"

    def print(self):
        """Provide a human-readable response."""
        print(f"preview located at {self.file_path}")
