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
        if nickname == "":
            self.window.set_login_error("Nickname cannot be empty")
            return
        self.window.set_login_error("")
        request.user = nickname
        self.client.socket.send(pickle.dumps(request))      
        response: Response = pickle.loads(self.client.socket.recv(self.client.buffer_size))
        if response.success:
            self.window.show_frame(self.window.menu_main_frame)
            return
        self.window.set_login_error(response.error)
            
    def join_game_action(self):
        pass

    def create_game_action(self):
        request = Request(user=self.window.username.get(), command="create_game")
        
        if True: # change this to response.success after we get response
            self.window.generate_game_frame()
            self.window.show_frame(self.window.game_main_frame)

    def make_move_action(self, move):
        # here will send move to server
        pass

        
    login = login_action
    join_game = join_game_action
    create_game = create_game_action
    
