from __future__ import annotations
from threading import Thread
from time import sleep
from tkinter import *
from tkinter.ttk import *
from ctypes import windll
from sv_ttk import use_dark_theme

from .Requests import Requests
from .Client import Client
from client.game_to_join import GameToJoin

windll.shcore.SetProcessDpiAwareness(1) # fix blurry font

class Window:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title("Rock, paper, scissors")
        use_dark_theme()
        
        self.client = Client(self)
        self.requests = Requests(self, self.client)
        self.client.start_response_thread()
        self.generate_login_frame()
        self.init_variables()
        
        self.root.protocol("WM_DELETE_WINDOW", self.requests.close_window)

    def show_frame(self, frame_to_show: Frame):
        self.current_frame.pack_forget()
        self.current_frame = frame_to_show
        self.current_frame.pack()
        
    def run(self):
        self.current_frame = self.login_main_frame
        self.current_frame.pack()
        self.root.mainloop()
        
    def set_error(self, error: str, error_widget: Text):
        error_widget.config(state="normal")
        error_widget.delete("1.0", END)
        error_widget.insert(INSERT, error)
        error_widget.config(state="disabled")
        
    def init_variables(self):
        self.game_name = StringVar(master=self.root)
        self.wins_required = IntVar(master=self.root, value=1)
        self.password = StringVar(master=self.root)
        self.game_owner = BooleanVar(master=self.root, value=False)
        self.play_again_status = BooleanVar(master=self.root, value=False)

    def generate_login_frame(self):
        self.login_main_frame = Frame(master=self.root)
        self.username = StringVar(master=self.root)
        Label(master=self.login_main_frame, text="Enter username", font=(25)).grid(row=0, column=0, padx=5, pady=100)
        Entry(master=self.login_main_frame, textvariable=self.username, width=50).grid(row=1, column=0, padx=5, pady=10)
        Button(master=self.login_main_frame, text="Log in", command=self.requests.login).grid(row=2, column=0, padx=5, pady=10)
        self.login_errors = Text(master=self.login_main_frame, fg="red", state="disabled", borderwidth=0)
        self.login_errors.bindtags((str(self.login_errors), str(self.root), "all"))
        self.login_errors.grid(row=3, column=0, pady=10)
        
    def generate_menu_frame(self):
        self.menu_main_frame = Frame(master=self.root)
        Button(master=self.menu_main_frame, text="Join game", command=self.generate_join_game_frame_with_refresh, width=50).grid(row=0, column=0, padx=5, pady=50)
        Button(master=self.menu_main_frame, text="Create game", command=self.generate_create_game_frame, width=50).grid(row=1, column=0, padx=5, pady=50)
        
    
    def generate_join_game_frame_with_refresh(self):
        self.generate_join_game_frame([])
        thread = RefreshGamesThread(self)
        thread.start()
    
    def generate_join_game_frame(self, available_games: list):
        self.join_game_main_frame = Frame(master=self.root)
        Button(master=self.join_game_main_frame, text="Cancel", command=lambda: self.show_frame(self.menu_main_frame), width=50).grid(row=0, column=0, padx=5, pady=50)
        for i in range(len(available_games)):
            game = GameToJoin(self, self.requests, available_games[i])
            game.generate_game_to_join(i+2)
        self.show_frame(self.join_game_main_frame)
        
        
    def generate_create_game_frame(self):
        self.create_game_main_frame = Frame(master=self.root)
        self.game_name = StringVar(master=self.root)
        self.wins_required = IntVar(master=self.root, value=1)
        self.password = StringVar(master=self.root)
        
        Label(master=self.create_game_main_frame, text="Game name", font=(25)).grid(row=0, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.game_name, width=50).grid(row=1, column=0, padx=5, pady=20)
        Label(master=self.create_game_main_frame, text="Required wins", font=(25)).grid(row=2, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.wins_required, width=50).grid(row=3, column=0, padx=5, pady=20)
        Label(master=self.create_game_main_frame, text="Password", font=(25)).grid(row=4, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.password, width=50).grid(row=5, column=0, padx=5, pady=20)
        Button(master=self.create_game_main_frame, text="Create Game", command=self.requests.create_game, width=50).grid(row=6, column=0, padx=5, pady=20)
        Button(master=self.create_game_main_frame, text="Cancel", command=lambda: self.show_frame(self.menu_main_frame), width=50).grid(row=7, column=0, padx=5, pady=20)
        self.create_game_errors = Text(master=self.create_game_main_frame, fg="red", state="disabled", borderwidth=0)
        
        self.create_game_errors.bindtags((str(self.login_errors), str(self.root), "all"))
        self.create_game_errors.grid(row=8, column=0, padx=5, pady=10)
        
        self.show_frame(self.create_game_main_frame)

    def generate_game_frame(self, opponent = "Waiting for opponent...", state="disabled"):
        self.game_main_frame = Frame(master=self.root)
        self.opponent_username = StringVar(master=self.root, value=opponent)
        self.choice = StringVar(master=self.root)
        self.score = IntVar(master=self.root, value=0)
        self.server_choice = StringVar(master=self.root)
        self.opponent_choice = StringVar(master=self.root)
        self.opponent_score = IntVar(master=self.root, value=0)
        self.winner = StringVar(master=self.root)

        # game name
        Label(master=self.game_main_frame, text=f"Game name:", font=(25)).grid(row=0, column=1, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.game_name, font=(25)).grid(row=1, column=1, padx=5, pady=0)
        
        Label(master=self.game_main_frame, text="You:", font=(25)).grid(row=2, column=0, padx=5, pady=10)
        Label(master=self.game_main_frame, text="Opponent:", font=(25)).grid(row=2, column=2, padx=5, pady=10)
        
        Label(master=self.game_main_frame, textvariable=self.username, font=(25)).grid(row=3, column=0, padx=5, pady=0)
        Label(master=self.game_main_frame, textvariable=self.opponent_username, font=(25)).grid(row=3, column=2, padx=5, pady=00)

        self.game_errors = Text(master=self.game_main_frame, fg="red", state="disabled", borderwidth=0)
        self.game_errors.bindtags((str(self.game_errors), str(self.root), "all"))
        self.game_errors.grid(row=14, column=1)
        
        # here moves will be displayed (text or img)
        Label(master=self.game_main_frame, text="Your move:", font=(25)).grid(row=4, column=0, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.server_choice, font=(25)).grid(row=5, column=0, padx=5, pady=10)
        Label(master=self.game_main_frame, text="Opponent's move:", font=(25)).grid(row=4, column=2, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.opponent_choice, font=(25)).grid(row=5, column=2, padx=5, pady=10)
        
        # button controls
        self.game_button_rock = Button(master=self.game_main_frame, text='Rock', command=lambda: self.choice.set("rock"), width=33, state=state)
        self.game_button_rock.grid(row=6, column=0, padx=2, pady=5)
        self.game_button_paper = Button(master=self.game_main_frame, text='Paper', command=lambda: self.choice.set("paper"), width=33, state=state)
        self.game_button_paper.grid(row=6, column=1, padx=2, pady=5)
        self.game_button_scissors = Button(master=self.game_main_frame, text='Scissors', command=lambda: self.choice.set("scissors"), width=33, state=state)
        self.game_button_scissors.grid(row=6, column=2, padx=2, pady=5)
        
        Label(master=self.game_main_frame, text="Selected move: ", font=(25)).grid(row=7, column=1, padx=5, pady=20)
        Label(master=self.game_main_frame, textvariable=self.choice, font=(25)).grid(row=8, column=1, padx=5, pady=0)
        
        self.game_button_confirm = Button(master=self.game_main_frame, text='Confirm', command=self.requests.make_move, width=33, state=state)
        self.game_button_confirm.grid(row=9, column=1, padx=2, pady=10)

        Label(master=self.game_main_frame, text=f"Score (required wins: {self.wins_required.get()})", font=(25)).grid(row=10, column=0, columnspan=2, padx=5, pady=20)
        Label(master=self.game_main_frame, text=f"Winner", font=(25)).grid(row=10, column=2, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.winner, font=(25)).grid(row=11, column=2, padx=5, pady=10)
        self.game_button_play_again = Button(master=self.game_main_frame, text='Play Again', command= lambda: self.requests.play_again(True), width=33)
        Label(master=self.game_main_frame, text="You: ", font=(25)).grid(row=11, column=0, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.score, font=(25)).grid(row=11, column=1, padx=5, pady=0)
        Label(master=self.game_main_frame, text="Opponent: ", font=(25)).grid(row=12, column=0, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.opponent_score, font=(25)).grid(row=12, column=1, padx=5, pady=0)
        
        self.game_button_leave = Button(master=self.game_main_frame, text='Leave', command=self.requests.leave_game, width=33)
        self.game_button_leave.grid(row=13, column=1, padx=5, pady=10)

class RefreshGamesThread(Thread):
    def __init__(self, window: Window, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.window = window


    def run(self):
        while self.window.current_frame == self.window.join_game_main_frame and self.window.root.winfo_exists():
            print("Refreshing list of games")
            self.window.requests.get_games()
            sleep(10)
