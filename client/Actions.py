from threading import Thread
from tkinter import W
from typing import TYPE_CHECKING

from request import Request

if TYPE_CHECKING:
    from .Window import Window
    from .Client import Client
    from game_data import GameData

class Actions:
            
    def __init__(self, window: 'Window', client: 'Client') -> None:
        self.window = window
        self.client = client
    
    def login(self):
        nickname = self.window.username.get()
        error_widget = self.window.login_errors
        if nickname == "":
            self.window.set_error("Nickname cannot be empty", error_widget)
            return
        self.window.set_error("", error_widget)
        request = Request(command="login", user=nickname)
        response = self.client.send_request(request)
        if response.success:
            self.window.show_frame(self.window.menu_main_frame)
            return
        self.window.set_error(response.error, error_widget)
    
    def join_game(self, game_name):
        request = Request(user=self.window.username.get(), command="join_game")
        request.data = {
            "game_name": game_name
        }
        response = self.client.send_request(request)
        self.window.game_name.set(game_name)
        if response.success:
            self.window.generate_game_frame(wait_for_opponent=False, opponent=response.data["opponent"], state="normal")
            self.window.show_frame(self.window.game_main_frame)
            return

    def get_games(self) -> list['GameData']:
        request = Request(user=self.window.username.get(), command="get_games")
        response = self.client.send_request(request)
        games = []
        try: games = response.data["games"]
        except Exception as e: print(e)
        return games


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
        response = self.client.send_request(request)
        
        if response.success:
            self.window.generate_game_frame()
            self.window.show_frame(self.window.game_main_frame)
            return
        self.window.set_error(response.error, error_widget)

    def make_move(self):
        self.window.game_button_confirm.config(state="disabled")
        self.window.choice.set('')
        request = Request(user=self.window.username.get(), command="make_move")
        request.data = {
            "choice": self.window.choice.get()
        }
        response = self.client.send_request(request)
        if response.success:
            thread = WaitForOpponentMoveThread(self.window)
            thread.start()


class WaitForOpponentMoveThread(Thread):
    def __init__(self, window: 'Window', group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.window = window
    
    def run(self) -> None:
        score = self.window.client.wait_for_response()
        if not score.success:
            return
        players = list(score.data.keys())
        if self.window.username.get() == players[0]:
            self.window.score.set(score.data[players[0]])
            self.window.opponent_score.set(score.data[players[1]])
        else:
            self.window.score.set(score.data[players[1]])
            self.window.opponent_score.set(score.data[players[0]])
            
        if self.window.username.get() in players[2]:
            self.window.server_choice.set(score.data[players[2]])
            self.window.opponent_choice.set(score.data[players[3]])
        else:
            self.window.server_choice.set(score.data[players[3]])
            self.window.opponent_choice.set(score.data[players[2]])
            
        self.window.game_button_confirm.config(state="normal")
