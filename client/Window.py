from __future__ import annotations
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING
from tkinter import *
from tkinter.ttk import *
from ctypes import windll
from sv_ttk import use_dark_theme

if TYPE_CHECKING:
    from game_data import GameData

from .Client import Client
from .Actions import Actions
from client.game_to_join import GameToJoin

windll.shcore.SetProcessDpiAwareness(1) # fix blurry font

class Window:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title("Rock, paper, scissors")
        use_dark_theme()
        
        self.client = Client(self)
        self.actions = Actions(self, self.client)
        
        self.generate_menu_frame()
        self.generate_login_frame()
        self.generate_create_game_frame()

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

    def generate_login_frame(self):
        self.login_main_frame = Frame(master=self.root)
        self.username = StringVar(master=self.root)
        Label(master=self.login_main_frame, text="Enter username", font=(25)).grid(row=0, column=0, padx=5, pady=100)
        Entry(master=self.login_main_frame, textvariable=self.username, width=50).grid(row=1, column=0, padx=5, pady=10)
        Button(master=self.login_main_frame, text="Log in", command=self.actions.login).grid(row=2, column=0, padx=5, pady=10)
        self.login_errors = Text(master=self.login_main_frame, fg="red", state="disabled", borderwidth=0)
        self.login_errors.bindtags((str(self.login_errors), str(self.root), "all"))
        self.login_errors.grid(row=3, column=0, pady=10)
        
    def generate_menu_frame(self):
        self.menu_main_frame = Frame(master=self.root)
        Button(master=self.menu_main_frame, text="Join game", command=self.generate_join_game_frame_with_refresh, width=50).grid(row=0, column=0, padx=5, pady=50)
        Button(master=self.menu_main_frame, text="Create game", command=lambda: self.show_frame(self.create_game_main_frame), width=50).grid(row=1, column=0, padx=5, pady=50)
    
    def generate_join_game_frame_with_refresh(self):
        self.generate_join_game_frame([])
        thread = RefreshGamesThread(self)
        thread.start()
    
    def generate_join_game_frame(self, available_games):
        self.join_game_main_frame = Frame(master=self.root)
        Button(master=self.join_game_main_frame, text="Cancel", command=lambda: self.show_frame(self.menu_main_frame), width=50).grid(row=0, column=0, padx=5, pady=50)
        for i in range(len(available_games)):
            game = GameToJoin(self, self.actions, available_games[i])
            game.generate_game_to_join(i+2)
        self.show_frame(self.join_game_main_frame)
        
        
    def generate_create_game_frame(self):
        self.create_game_main_frame = Frame(master=self.root)
        self.game_name = StringVar(master=self.root)
        self.wins_required = IntVar(master=self.root, value=1)
        self.password = StringVar(master=self.root)
        #TODO check if non-empty, replace wins with number, validate
        Label(master=self.create_game_main_frame, text="Game name", font=(25)).grid(row=0, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.game_name, width=50).grid(row=1, column=0, padx=5, pady=20)
        Label(master=self.create_game_main_frame, text="Required wins", font=(25)).grid(row=2, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.wins_required, width=50).grid(row=3, column=0, padx=5, pady=20)
        Label(master=self.create_game_main_frame, text="Password", font=(25)).grid(row=4, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.password, width=50).grid(row=5, column=0, padx=5, pady=20)
        Button(master=self.create_game_main_frame, text="Create Game", command=self.actions.create_game).grid(row=6, column=0, padx=5, pady=75)
        Button(master=self.create_game_main_frame, text="Cancel", command=lambda: self.show_frame(self.menu_main_frame), width=50).grid(row=7, column=0, padx=5, pady=50)
        self.create_game_errors = Text(master=self.create_game_main_frame, fg="red", state="disabled", borderwidth=0)
        self.create_game_errors.bindtags((str(self.login_errors), str(self.root), "all"))
        self.create_game_errors.grid(row=7, column=0, padx=5, pady=10)

    def generate_game_frame(self, wait_for_opponent = True, opponent = "Waiting for opponent...", state="disabled"):
        self.game_main_frame = Frame(master=self.root)
        self.opponent_username = StringVar(master=self.root, value=opponent)
        self.choice = StringVar(master=self.root)
        self.score = IntVar(master=self.root, value=0)
        self.server_choice = StringVar(master=self.root)
        self.opponent_choice = StringVar(master=self.root)
        self.opponent_score = IntVar(master=self.root, value=0)
        # game name
        Label(master=self.game_main_frame, text=f"Game name:", font=(25)).grid(row=0, column=1, columnspan=2, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.game_name, font=(25)).grid(row=1, column=1, columnspan=2, padx=5, pady=0)
        
        Label(master=self.game_main_frame, text="You:", font=(25)).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        Label(master=self.game_main_frame, text="Opponent:", font=(25)).grid(row=2, column=2, columnspan=2, padx=5, pady=10)
        
        Label(master=self.game_main_frame, textvariable=self.username, font=(25)).grid(row=3, column=0, columnspan=2, padx=5, pady=0)
        Label(master=self.game_main_frame, textvariable=self.opponent_username, font=(25)).grid(row=3, column=2, columnspan=2, padx=5, pady=00)

        # here moves will be displayed (text or img)
        Label(master=self.game_main_frame, text="Your move:", font=(25)).grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.server_choice, font=(25)).grid(row=5, column=0, columnspan=2, padx=5, pady=10)
        Label(master=self.game_main_frame, text="Opponent's move:", font=(25)).grid(row=4, column=2, columnspan=2, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.opponent_choice, font=(25)).grid(row=5, column=2, columnspan=2, padx=5, pady=10)
        
        # button controls
        self.game_button_rock = Button(master=self.game_main_frame, text='Rock', command=lambda: self.choice.set("rock"), width=33, state=state)
        self.game_button_rock.grid(row=6, column=0, padx=2, pady=5)
        self.game_button_paper = Button(master=self.game_main_frame, text='Paper', command=lambda: self.choice.set("paper"), width=33, state=state)
        self.game_button_paper.grid(row=6, column=1, padx=2, pady=5)
        self.game_button_scissors = Button(master=self.game_main_frame, text='Scissors', command=lambda: self.choice.set("scissors"), width=33, state=state)
        self.game_button_scissors.grid(row=6, column=2, padx=2, pady=5)
        
        Label(master=self.game_main_frame, text="Selected move: ", font=(25)).grid(row=7, column=1, columnspan=2, padx=5, pady=20)
        Label(master=self.game_main_frame, textvariable=self.choice, font=(25)).grid(row=8, column=1, columnspan=2, padx=5, pady=0)
        
        self.game_button_confirm = Button(master=self.game_main_frame, text='Confirm', command=self.actions.make_move, width=33, state=state)
        self.game_button_confirm.grid(row=9, column=1, padx=2, pady=10)

        Label(master=self.game_main_frame, text=f"Score (required wins: {self.wins_required.get()})", font=(25)).grid(row=10, column=0, columnspan=2, padx=5, pady=20)
        Label(master=self.game_main_frame, text=f"Winner", font=(25)).grid(row=10, column=2, padx=5, pady=10)
        Label(master=self.game_main_frame, text="You: ", font=(25)).grid(row=11, column=0, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.score, font=(25)).grid(row=11, column=1, padx=5, pady=0)
        Label(master=self.game_main_frame, text="Opponent: ", font=(25)).grid(row=12, column=0, padx=5, pady=10)
        Label(master=self.game_main_frame, textvariable=self.opponent_score, font=(25)).grid(row=12, column=1, padx=5, pady=0)
        
        #TODO add leave game button and handle  

        if wait_for_opponent:
            thread = WaitForOpponentJoinThread(self)
            thread.start()

class RefreshGamesThread(Thread):
    def __init__(self, window: Window, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.window = window
        self.current_games = []
        self.all_games = []
        self.games_to_render = []
        self.games_to_remove = []

    def run(self):
        while self.window.current_frame == self.window.join_game_main_frame:
            #TODO rework the thread to only rerender new games/remove deleted ones
            self.current_games = self.window.actions.get_games()
            self.window.generate_join_game_frame(self.current_games)
            sleep(10)
            
class WaitForOpponentJoinThread(Thread):
    
    def __init__(self, window: Window, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.window = window
    
    def run(self) -> None:
        opponent_data = self.window.client.wait_for_response()
        if not opponent_data.success:
            return
        self.window.opponent_username.set(opponent_data.data["opponent"])
        self.window.game_button_rock.config(state="normal")
        self.window.game_button_paper.config(state="normal")
        self.window.game_button_scissors.config(state="normal")
        self.window.game_button_confirm.config(state="normal")
        self.window.choice.set('')
        
