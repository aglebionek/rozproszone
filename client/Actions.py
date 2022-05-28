from typing import TYPE_CHECKING
import pickle

from request import Request
from response import Response

if TYPE_CHECKING:
    from .Window import Window
    from .Client import Client

class Actions:
            
    def __init__(self, window: 'Window', client: 'Client') -> None:
        self.window = window
        self.client = client
    
    def login_action(self):
        nickname = self.window.username.get()
        request = Request(command="login")
        error_widget = self.window.login_errors
        if nickname == "":
            self.window.set_error("Nickname cannot be empty", error_widget)
            return
        self.window.set_error("", error_widget)
        request.user = nickname
        self.client.socket.send(pickle.dumps(request))      
        response: Response = pickle.loads(self.client.socket.recv(self.client.buffer_size))
        if response.success:
            self.window.show_frame(self.window.menu_main_frame)
            return
        self.window.set_error(response.error, error_widget)
            
    def join_game_action(self):
        pass

    def create_game_action(self):
        request = Request(user=self.window.username.get(), command="create_game")
        request.data = {
            "game_name": self.window.game_name,
            "req_wins": self.window.wins_required,
            "game_password": self.window.password
        }
        self.client.socket.send(pickle.dumps(request))


    login = login_action
    join_game = join_game_action
    create_game = create_game_action
    
