import pickle
import socket
import traceback
from threading import Thread, Lock

from game_data import GameData
from request import Request
from response import Response

buf = 1024

class Server:
    users: dict[str, socket.socket] = {}
    games: dict[str, GameData] = {}
    
    def __init__(self) -> None:
        self.host = "localhost"
        self.port = 8080
        self.addr = (self.host, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def run(self):
        self.socket.bind(self.addr)
        self.socket.listen(10)
        print(f"Server is listening for connections at address: {self.addr}")
        while True:
            client, address = self.socket.accept()
            thread = Server.UserThread(kwargs={"client": client, "address": address})
            thread.start()

    class UserThread(Thread):
        def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
            super().__init__(group, target, name, args, kwargs, daemon=daemon)
            self.client: socket.socket = kwargs["client"]
            self.address: tuple = kwargs["address"]
            self.game_name = ""
            self.user = ""
            self.lock: Lock = Lock()
            self.game_owner = False
        
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
            
        def determine_winner(self, game_data: GameData):
            player1_choice = game_data.player1_choice
            player2_choice = game_data.player2_choice
            
            player1 = game_data.player1
            player2 = game_data.player2
            
            player1_choices = {
                "rock": 1,
                "paper": 3,
                "scissors": 7
            }
            
            player2_choices = {
                "rock": 15,
                "paper": 31,
                "scissors": 63
            }

            winner_table = {
                "16": '',
                "34": '',
                "70": '',
                "18": player1,
                "38": player1,
                "64": player1,
                "22": player2,
                "32": player2,
                "66": player2,
            }
            
            winner = winner_table[str(player1_choices[player1_choice]+player2_choices[player2_choice])]
            print(f"Winner: {winner}")
            
            self.lock.acquire()
            Server.games[self.game_name] = game_data
            self.lock.release()
            
            return winner
        
        def run(self):
            print(f"New thread created for accepted connection from: {self.address}")
            while not Server.UserThread.is_socket_closed(self.client):
                response: Response = Response(success=False) # initial response for the request
                try:
                    bytes = self.client.recv(buf) # wait for a request
                    request: Request = pickle.loads(bytes) # decode the request
                    if request.command != "get_games": print(request)
                    if request.command == "login":
                        if request.user in Server.users.keys():
                            response.error = "A user with that name is already logged in. Please change the name and try again."
                            self.client.send(pickle.dumps(response))
                            continue
                        
                        self.lock.acquire()
                        Server.users[request.user] = self.client
                        self.lock.release()
                        
                        self.user = request.user
                    elif request.command == "create_game":
                        response.data = {"game_created": True}
                        
                        self.game_name = request.data["game_name"]
                        
                        self.lock.acquire()
                        games = Server.games.keys()
                        self.lock.release()
                        
                        if self.game_name in games:
                            response.error = "A game with that name already exists. Please try a different name."
                            self.client.send(pickle.dumps(response))
                            continue
                        
                        game_data = GameData(
                            player1=self.user, 
                            game_name=self.game_name,
                            wins_required=request.data["req_wins"])
                        game_data.game_owner=self.user
                        game_data.password = request.data["game_password"]
                        
                        self.lock.acquire()
                        Server.games[self.game_name] = game_data
                        self.lock.release()
                        
                        self.game_owner = True
                    elif request.command == "join_game":
                        self.game_name = request.data["game_name"]
                        
                        self.lock.acquire()
                        game_data = Server.games[self.game_name]
                        game_data.player2 = request.user
                        Server.games[self.game_name] = game_data
                        Server.users[game_data.player1].send(pickle.dumps(Response(True, {"opponent": request.user})))
                        self.lock.release()
                        
                        response.data = {"opponent": game_data.player1}
                    elif request.command == "get_games":
                        response.data["games"] = []
                        self.lock.acquire()
                        print("Getting games...")
                        response.data = {
                            "games": [game for game in list(Server.games.values()) if game.player2 == '']
                        }
                        print("Games got, sending...")
                        self.lock.release()
                    elif request.command == "play_again":
                        
                        game_data.player1_choice = ''
                        game_data.player2_choice = ''
                        game_data.player1_wins = 0
                        game_data.player2_wins = 0
                        game_data.winner = ''
                        
                        # if guest didn't leave
                        if game_data.player2 != '':
                            Server.users[game_data.player2].send(pickle.dumps(Response(True, {"play_again": True})))
                            response.data = {"play_again": True}
                        else:
                            response.data = {"play_again": False}
                    elif request.command == "make_move":
                        response.data = {"make_move": True}
                        
                        try:
                            self.lock.acquire()
                            game_data = Server.games[self.game_name]
                            self.lock.release()
                        except KeyError:
                            self.lock.release()
                            print("The game doesn't exist anymore, resetting...")
                            response.success = True
                            response.data = {
                                "host_left": True
                            }
                            self.client.send(pickle.dumps(response))
                            continue 
                        
                        if game_data.player2 == '':
                            print("The guest left, resetting...")
                            response.success = True
                            response.data = {
                                "guest_left": True
                            }
                            self.client.send(pickle.dumps(response))
                            continue 
                        
                        if game_data.player1 == self.user:
                            game_data.player1_choice = request.data["choice"]
                        else:
                            game_data.player2_choice = request.data["choice"]
                        
                        if game_data.player1_choice != "" and game_data.player2_choice != "":
                            winner = self.determine_winner(game_data)
                            
                            if winner == game_data.player1:
                                game_data.player1_wins+=1
                            elif winner == game_data.player2:
                                game_data.player2_wins+=1
                                
                            score = {
                                game_data.player1: game_data.player1_wins,
                                game_data.player2: game_data.player2_wins,
                                f"{game_data.player1}_choice": game_data.player1_choice,
                                f"{game_data.player2}_choice": game_data.player2_choice
                            }
                            
                            game_data.player1_choice = ''
                            game_data.player2_choice = ''
                            
                            if game_data.player1_wins == game_data.wins_required:
                                score["winner"] = game_data.player1
                                score["game_owner"] = game_data.game_owner
                            elif game_data.player2_wins == game_data.wins_required:
                                score["winner"] = game_data.player2
                                score["game_owner"] = game_data.game_owner
                                

                            response.success = True
                            self.client.send(pickle.dumps(response))
                            
                            print("Round concluded, sending game results")
                            Server.users[game_data.player1].send(pickle.dumps(Response(True, score)))
                            Server.users[game_data.player2].send(pickle.dumps(Response(True, score)))
                            
                            continue
                        
                    elif request.command == "leave_game":
                        response.data = {"leave_game": True}
                        print(f"{self.user} left the game {self.game_name}")
                        try:
                            self.lock.acquire()
                            game_data = Server.games[self.game_name]
                            self.lock.release()
                        except KeyError:
                            self.lock.release()
                            print("The game doesn't exist anymore, resetting...")
                            response.data = {
                                "host_left": True
                            }
                            self.client.send(pickle.dumps(response))
                            continue 
                        
                        if request.user == game_data.game_owner:
                            self.lock.acquire()
                            del Server.games[self.game_name]
                            self.lock.release()
                            print(f"removed game {self.game_name}")
                            if game_data.player2 != '':
                                Server.users[game_data.player2].send(pickle.dumps(Response(True, {"left": "host"})))
                                
                        else:
                            game_data.player1_choice = ''
                            game_data.player2_choice = ''
                            game_data.player1_wins = 0
                            game_data.player2_wins = 0
                            game_data.winner = ''
                            game_data.player2 = ''
                            
                            # if game_data.player1 != '':
                            #     Server.users[game_data.player1].send(pickle.dumps(Response(True, {"left": "guest"})))
                                
                        self.game_name = ''

                    response.success = True
                    self.client.send(pickle.dumps(response))
                except Exception as e:
                    print("Exception caught")
                    print(e, traceback.format_exc())
                    response.success = False
                    response.error = e
                    try: self.client.send(pickle.dumps(response))
                    except OSError as os_e:
                        print("OS Exception caught")
                        print(os_e, traceback.format_exc())
                    print(f"Thread broke for user {self.user}, please restart client")
                    break
                    

            self.lock.acquire()
            try: 
                del Server.users[self.user]
                print(f"Removed user {self.user}")
            except Exception as e: 
                print(e, traceback.format_exc())
                
            if self.game_owner:
                try: 
                    del Server.games[self.game_name]
                    print(f"Removed game {self.game_name}")
                except Exception as e:
                    print(e, traceback.format_exc())
                
            self.lock.release()
            self.client.close()
            print(f"{self.address} - {self.user} disconnected successfully, closing thread.")
