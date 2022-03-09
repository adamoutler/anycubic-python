"""A message inheritance demo."""
class BaseResponse:
    """base response"""
    message="foo"

class Response1(BaseResponse):
    """The first response inherits the message from BaseResponse."""
    var1=None
    def __init__(self, one):
        self.var1=one

class Response2(BaseResponse):
    """The second response inherits the message"""
    var2=None
    def __init__(self, two):
        self.var2=two

def detect(value)->BaseResponse:
    """detect the value and send a proper response"""
    if value=="1":
        return Response1(1)
    if value=="2":
        return Response2(2)
    return BaseResponse

response=detect("1")
if isinstance(response,Response1):
    print(response.var2)
if isinstance(response,Response2):
    print(response.var2)


