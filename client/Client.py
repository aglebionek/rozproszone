import socket
import pickle
from threading import Thread
import traceback

from request import Request

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Window import Window
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
    
    def send_request(self, request: Request) -> None:
        self.socket.send(pickle.dumps(request))
    
    def get_response(self) -> 'Response':
        return pickle.loads(self.socket.recv(self.buffer_size))
    
    def start_response_thread(self) -> None:
        self.response_thread = ResponseThread(self.window)
        self.response_thread.start()


class ResponseThread(Thread):
    
    @staticmethod
    def is_socket_closed(sock: socket.socket) -> bool:
        try:
            # this will try to read bytes without blocking and also without removing them from buffer (peek only)
            sock.setblocking(1)
            data = sock.recv(16, socket.MSG_PEEK)
            return len(data) == 0
        except ConnectionResetError:
            return True  # socket was closed for some other reason
        except BlockingIOError:
            return False  # socket is open and reading from it would block
        except Exception as e:
            print(e)
            return False
    
    def __init__(self, window: 'Window', group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.window = window
        self.client = self.window.client
        self.requests = self.window.requests
        
    def kill(self):
        self.client.send_request(Request(command="kill_thread"))
        
    def run(self):
        while not ResponseThread.is_socket_closed(self.client.socket):
            try:
                print("Waiting for response...")
                response = self.client.get_response()
                print("Recieved response in thread")
                print(response)
                
                if response.error != '':
                    print("Server returned an error")
                    print(response.error)
                
                if response.command == "kill_thread":
                    self.client.socket.close()
                    break
                
                if response.command == "login":
                    if not response.error:
                        self.window.generate_menu_frame()
                        self.window.show_frame(self.window.menu_main_frame)
                        continue
                    self.window.set_error(response.error, self.window.login_errors)
                    
                
                elif response.command == "create_game":
                    if not response.error:
                        self.window.generate_game_frame()
                        self.window.show_frame(self.window.game_main_frame)
                        self.window.game_owner.set(True)
                        continue
                    self.window.set_error(response.error, self.window.create_game_errors)
                    
                    
                elif response.command == "join_game":
                    if not response.error:
                        
                        self.window.generate_game_frame(opponent=response.data["opponent"], state="normal")
                        self.window.game_name.set(response.data["game_name"])
                        self.window.show_frame(self.window.game_main_frame)

                
                elif response.command == "opponent_joined":
                    if not response.error:
                        self.window.opponent_username.set(response.data["opponent"])
                        self.window.game_button_rock.config(state="normal")
                        self.window.game_button_paper.config(state="normal")
                        self.window.game_button_scissors.config(state="normal")
                        self.window.game_button_confirm.config(state="normal")
                        self.window.choice.set('')
                
                
                elif response.command == "get_games":
                    if not response.error:
                        games = []
                        try: games = response.data["games"]
                        except Exception as e: print(e, traceback.format_exc())
                        self.window.generate_join_game_frame(games)

                
                elif response.command == "round_concluded":
                    if not response.error:
                        self.window.score.set(response.data[f"{self.window.username.get()}_wins"])
                        self.window.opponent_score.set(response.data[f"{self.window.opponent_username.get()}_wins"])
                        self.window.server_choice.set(response.data[f"{self.window.username.get()}_choice"])
                        self.window.opponent_choice.set(response.data[f"{self.window.opponent_username.get()}_choice"])
                        self.window.choice.set('')
                        
                        if "winner" in response.data.keys():
                            self.window.winner.set(response.data["winner"])
                            self.window.play_again_status.set(True)
                            if self.window.game_owner.get():
                                self.window.game_button_play_again.grid(row=12, column=2, padx=5, pady=10)
                        else:
                            self.window.game_button_confirm.config(state="normal")
                            self.window.game_button_rock.config(state="normal")
                            self.window.game_button_paper.config(state="normal")
                            self.window.game_button_scissors.config(state="normal")
                            
                            
                elif response.command == "play_again":
                    if not self.window.play_again_status.get(): continue
                    
                    if not response.error:
                        if response.data["play_again"]:
                            self.window.choice.set('')
                            self.window.server_choice.set('')
                            self.window.opponent_choice.set('')
                            self.window.score.set(0)
                            self.window.opponent_score.set(0)
                            self.window.winner.set('')
                            self.window.game_button_confirm.config(state="normal")
                            self.window.game_button_rock.config(state="normal")
                            self.window.game_button_paper.config(state="normal")
                            self.window.game_button_scissors.config(state="normal")
                            if self.window.game_owner.get():
                                self.window.game_button_play_again.grid_remove()
                        else:
                            self.requests.leave_game()
                            
                        self.window.play_again_status.set(False)
                    
                    
                elif response.command == "leave_game":
                    if not response.error:
                        self.window.play_again_status.set(False)
                        
                        if response.data["left"] == "host":
                            self.window.generate_menu_frame()
                            self.window.show_frame(self.window.menu_main_frame)
                        elif response.data["left"] == "guest":
                            if self.window.game_owner.get():
                                self.window.generate_game_frame()
                                self.window.show_frame(self.window.game_main_frame)
                            else:
                                self.window.generate_menu_frame()
                                self.window.show_frame(self.window.menu_main_frame)
                        
            except Exception as e:
                print(e, traceback.format_exc())
                print("Unexpected error occured")
                
            
            
        print("Response thread killed")
        