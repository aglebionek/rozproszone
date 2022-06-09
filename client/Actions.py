from threading import Thread
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
        print(request)
        response = self.client.send_request(request)
        print(response)
        if response.success:
            self.window.generate_game_frame(wait_for_opponent=False, opponent=response.data["opponent"], state="normal")
            self.window.game_name.set(game_name)
            self.window.show_frame(self.window.game_main_frame)
            return

    def get_games(self) -> list['GameData']:
        request = Request(user=self.window.username.get(), command="get_games")
        response = self.client.send_request(request)
        games = []
        print("get games response", response)
        try: games = response.data["games"]
        except Exception as e: print(e)
        return games
    
    def close_window(self):
        try:
            if self.window.current_frame == self.window.game_main_frame:
                self.leave_game(change_window = False)
        except Exception as e:
            print(e, traceback.format_exc())
        finally:
            self.window.root.destroy()

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
        print("create game resopnse", response)
        if response.success:
            self.window.generate_game_frame()
            self.window.show_frame(self.window.game_main_frame)
            return
        self.window.set_error(response.error, error_widget)

    def make_move(self):
        error_widget = self.window.game_errors
        if self.window.choice.get() == '':
            self.window.set_error("pick your move", error_widget)
            return
        self.window.set_error("", error_widget)
        
        self.window.game_button_confirm.config(state="disabled")
        request = Request(user=self.window.username.get(), command="make_move")
        request.data = {
            "choice": self.window.choice.get()
        }
        response = self.client.send_request(request)
        print("make move response")
        print(response)
        if "host_left" or "left" in response.data.keys():
            print("host left")
            self.window.generate_menu_frame()
            self.window.show_frame(self.window.menu_main_frame)
            return
        
        if "guest_left" in response.data.keys():
            print("guest left")
            self.window.generate_game_frame()
            self.window.show_frame(self.window.game_main_frame)
            return 
                    
        if response.success:
            thread = WaitForOpponentMoveThread(self.window)
            thread.start()
            
    def leave_game(self, change_window = True):
        request = Request(user=self.window.username.get(), command="leave_game")
        response = self.client.send_request(request)
        self.waiting_for_opponent_to_join = False
        print("leave game response", response)
        if response.success:
            self.window.play_again_status.set(False)
            if change_window:
                self.window.generate_menu_frame()
                self.window.show_frame(self.window.menu_main_frame)
            
    def play_again(self, again: bool):
        if self.window.play_again_status.get(): return
        request = Request(user=self.window.username.get(), command="play_again")
        request.data = {
            "again": again
        }
        response = self.client.send_request(request)
        if response.success:
            if "play_again" in response.data.keys():
                self.window.choice.set('')
                self.window.server_choice.set('')
                self.window.opponent_choice.set('')
                self.window.score.set(0)
                self.window.opponent_score.set(0)
                self.window.winner.set('')
                self.window.game_button_confirm.config(state="normal")
            else:
                self.leave_game()
            
            try:
                self.window.game_button_play_again.grid_remove()
            except Exception:
                pass

class WaitForOpponentMoveThread(Thread):
    def __init__(self, window: 'Window', group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.window = window
    
    def run(self) -> None:
        score = self.window.client.get_response()
        print("Wait for opponent move thread read something")
        print(score)
        if not score.success:
            return
        
        try:
            players = list(score.data.keys())
            if "left" in players:
                if score.data["left"] == "guest":
                    print("guest left")
                    self.window.generate_game_frame()
                    self.window.show_frame(self.window.game_main_frame)
                else:
                    print("host left")
                    self.window.generate_menu_frame()
                    self.window.show_frame(self.window.menu_main_frame)
                return
            
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
                
            self.window.choice.set('')
                
            if "winner" in players:
                self.window.winner.set(score.data["winner"])
                if score.data["game_owner"] == self.window.username.get():
                    self.window.game_button_play_again.grid(row=12, column=2, padx=5, pady=10)
                else:
                    self.window.play_again_status.set(True)
                    thread = WaitForPlayAgainThread(self.window)
                    thread.start()
            else:
                self.window.game_button_confirm.config(state="normal")
        except Exception as e:
            print(e, traceback.format_exc())
            
        print("Wait for opponent thread ended")
        self.window.actions.waiting_for_opponent_to_join = False
        
        
        
class WaitForPlayAgainThread(Thread):
    def __init__(self, window: 'Window', group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.window = window
    
    def run(self) -> None:
        
        while self.window.play_again_status.get():
            print("Waiting for play again...")
            
            response = self.window.client.get_response()
            print("Wait for play again thread got something")
            print(response)
            
            if response.success:
                if "left" in response.data.keys():
                    if response.data["left"] == "host":
                        print("host left")
                        self.window.generate_menu_frame()
                        self.window.show_frame(self.window.menu_main_frame)
                    self.window.play_again_status.set(False)
                    break
                
                if "leave_game" in response.data.keys():
                    self.window.play_again_status.set(False)
                    print("here1")
                    self.window.generate_menu_frame()
                    print("here2")
                    self.window.show_frame(self.window.menu_main_frame)
                    print("here3")
                self.window.choice.set('')
                self.window.server_choice.set('')
                self.window.opponent_choice.set('')
                self.window.score.set(0)
                self.window.opponent_score.set(0)
                self.window.winner.set('')
                self.window.game_button_confirm.config(state="normal")
                
                try:
                    self.window.game_button_play_again.grid_remove()
                except Exception as e:
                    print(e, traceback.format_exc())

                
                self.window.play_again_status.set(False)
        
        print("Wait for play again thread ended")