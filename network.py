IP = "192.168.29.99"
PORT = 8000

# All possible events that can be sent between the server and the clients
EVENT_REG_UPDATE = 0            # Regular game update event. Only sent by the server
EVENT_PR_JOIN = 1               # Priority game joining event. Can be sent by the server and clients
EVENT_REG_INPUT = 2             # Input event. Only sent by the clients

class NetworkEvent:
    __slots__ = ('type', 'data')

    def __init__(self, eventType: int, eventData: dict) -> None:
        self.type: int = eventType
        self.data: dict = eventData