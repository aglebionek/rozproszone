import pickle
import socket
import uuid
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
            self.user: str = ""
            self.lock: Lock = Lock()
        
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
        
        def run(self):
            print(f"New thread created for accepted connection from: {self.address}")
            while not Server.UserThread.is_socket_closed(self.client):
                response: Response = Response(success=False)
                try:
                    bytes = self.client.recv(buf)
                    request: Request = pickle.loads(bytes)
                    print(request)
                    if request.command == "login":
                        if request.user in Server.users.keys():
                            response.error = "A user with that name is already logged in. Please change the name and try again."
                            self.client.send(pickle.dumps(response))
                            continue
                        
                        self.lock.acquire()
                        Server.users[request.user] = self.client
                        self.lock.release()
                        
                        self.user = request.user
                        response.success = True
                    elif request.command == "create_game":
                        #WIP
                        #this is gonna come with the game data, TODO check if the game_id doesn't already exist
                        self.game_name = request.data["game_name"]
                        print(Server.games)
                        if self.game_name in Server.games.keys():
                            response.error = "A game with that name already exists. Please try a different name."
                            self.client.send(pickle.dumps(response))
                            continue
                        
                        self.lock.acquire()
                        Server.games[self.game_name] = GameData(player1=self.user, game_name=self.game_name)
                        self.lock.release()
                        
                        response.success = True
                    elif request.command == "join_game":
                        game_id = request.data["game_id"]
                        # send client and game id
                        response.success = True
                    
                    self.client.send(pickle.dumps(response))
                except Exception as e:
                    print("Exception caught")
                    print(e)
                    response.success = False
                    response.error = e
                    try: self.client.send(pickle.dumps(response))
                    except OSError as os_e:
                        print("OS Exception caught")
                        print(os_e)
                    break

            self.lock.acquire()
            try: 
                del Server.users[self.user]
                print(f"Removed user {self.user}")
            except Exception as e: print(e)
            try: 
                del Server.games[self.game_name]
                print(f"Removed game {self.game_name}")
            except Exception as e: print(e)
            self.lock.release()
            self.client.close()
            print(f"{self.address} - {self.user} disconnected successfully, closing thread.")
            
            
    class GameThread(Thread):
        lock = Lock()
        
        choices = {
            "1": "rock",
            "3": "paper",
            "7": "scissors"
        }
        
        outcomes = {
            ""
        }
        
        @staticmethod
        def run(game_id: str, user: str):
            client = Server.users[user]
            
            bytes = client.recv(buf)
            request: Request = pickle.loads(bytes)
            #TODO 1. read sent data (player choice)
            #TODO 2. if it's the non game_owner thread, wait for another input
            #TODO 3. if it's the game_owner thread, calculate who won and and send a response updating the score and allowing new turn if nobody won