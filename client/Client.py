import socket
import pickle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Window import Window
    from request import Request
    from response import Response

class Client:
        
    def __init__(self, window: 'Window') -> None:
        self.window = window
        self.connect()
        
    def connect(self):
        self.buffer_size = 1024
        self.server_address = ("localhost", 8080)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.server_address)
    
    def send_request(self, request: 'Request') -> 'Response':
        self.socket.send(pickle.dumps(request))
        return self.wait_for_response()
    
    def wait_for_response(self) -> 'Response':
        return pickle.loads(self.socket.recv(self.buffer_size))