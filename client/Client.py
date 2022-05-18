import socket

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Window import Window

class Client:
        
    def __init__(self, window: 'Window') -> None:
        self.window = window
        self.connect()
        
    def connect(self):
        self.buffer_size = 1024
        self.server_address = ("localhost", 8080)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.server_address)
        
    def send_command_to_server(self, command: str):
        binary_command = command.encode()
        self.socket.send(binary_command)
            