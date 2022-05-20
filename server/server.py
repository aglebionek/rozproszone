import pickle
import socket
import uuid
from threading import Thread, Lock

from game_data import GameData
from request import Request
from response import Response

buf = 1024

class Server:
    users = [] # replace with dict where the key is the nickname and the value is the player socket?
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
            Thread(target = Server.UserThread.run, args = (client,address)).start()

    class UserThread(Thread):
        user = ""
        game_id = ""
        lock = Lock()

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
        
        @staticmethod
        def run(client: socket.socket, address):
            print(f"New thread created for accepted connection from: {address}")
            while not Server.UserThread.is_socket_closed(client):
                response: Response = Response(success=False)
                try:
                    bytes = client.recv(buf)
                    request: Request = pickle.loads(bytes)
                    print(request)
                    if request.command == "login":
                        Server.UserThread.lock.acquire()
                        
                        if request.user in Server.users:
                            response.error = "A user with that name is already logged in. Please change the name and try again."
                            client.send(pickle.dumps(response))
                            continue
                        Server.users.append(request.user)
                        
                        Server.UserThread.lock.release()
                        
                        Server.UserThread.user = request.user
                        response.success = True
                    elif request.command == "create_game":
                        #WIP
                        Server.UserThread.game_id = str(uuid.uuid4())
                        Server.UserThread.lock.acquire()
                        Server.games[Server.UserThread.game_id] = GameData(player1=Server.UserThread.user)
                        
                        Server.UserThread.lock.release()
                        response.success = True
                    elif request.command == "join_game":
                        #WIP
                        #if this happens, then we should start a new thread for the game (and kill this thread for the users in a game?)
                        pass    
                        
                except Exception as e:
                    response.error = e
                finally:
                    client.send(pickle.dumps(response))
            
            Server.UserThread.lock.acquire()
            Server.users.remove(Server.UserThread.user)
            Server.UserThread.lock.release()
            
            client.close()
            print(f"{address} - {Server.UserThread.user} disconnected, closing thread.")
            
    class GameThread(Thread):
        lock = Lock()
        #WIP



