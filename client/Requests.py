import traceback
from typing import TYPE_CHECKING
from request import Request

if TYPE_CHECKING:
    from .Window import Window
    from .Client import Client
    from game_data import GameData

class Requests:
            
    def __init__(self, window: 'Window', client: 'Client') -> None:
        self.window = window
        self.client = client
        self.waiting_for_opponent_to_join = False
        
        
    def close_window(self):
        try:
            if self.window.current_frame == self.window.game_main_frame:
                self.leave_game(change_window = False)
        except Exception as e:
            print(e, traceback.format_exc())
        finally:
            self.window.root.destroy()
            self.client.response_thread.kill()
    
    
    def login(self):
        nickname = self.window.username.get()
        error_widget = self.window.login_errors
        if nickname == "":
            self.window.set_error("Nickname cannot be empty", error_widget)
            return
        self.window.set_error("", error_widget)
        request = Request(command="login", user=nickname)
        self.client.send_request(request)


    def join_game(self, game_name):
        request = Request(user=self.window.username.get(), command="join_game")
        request.data = {"game_name": game_name}
        self.client.send_request(request)
        self.window.game_owner.set(False)


    def create_game(self):
        game_name = self.window.game_name.get()
        wins_required = self.window.wins_required.get()
        password = self.window.password.get()
        error_widget = self.window.create_game_errors

        game_name_empty = not game_name
        incorrect_wins_required = wins_required < 1
        if game_name_empty or incorrect_wins_required:
            error_message = "Game name cannot be empty\n"*game_name_empty + "Number of required wins must be greater than 0"*incorrect_wins_required
            self.window.set_error(error_message, error_widget)
            return
        self.window.set_error("", error_widget)
        
        request = Request(user=self.window.username.get(), command="create_game")
        request.data = {
            "game_name": game_name,
            "req_wins": wins_required,
            "game_password": password
        }
        self.client.send_request(request)
    

    def get_games(self) -> list['GameData']:
        request = Request(user=self.window.username.get(), command="get_games")
        self.client.send_request(request)
    
    
    def make_move(self):
        self.window.game_button_confirm.config(state="disabled")
        self.window.game_button_rock.config(state="disabled")
        self.window.game_button_paper.config(state="disabled")
        self.window.game_button_scissors.config(state="disabled")
        
        request = Request(user=self.window.username.get(), command="make_move")
        request.data = {"choice": self.window.choice.get()}
        self.client.send_request(request)
    
    
    def leave_game(self, change_window = True):
        request = Request(user=self.window.username.get(), command="leave_game")
        self.client.send_request(request)
    
    
    def play_again(self, again: bool):
        request = Request(user=self.window.username.get(), command="play_again")
        request.data = {"again": again}
        self.client.send_request(request)
