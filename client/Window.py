from __future__ import annotations
from tkinter import *
from tkinter.ttk import *
from ctypes import windll
from sv_ttk import use_dark_theme

from .Client import Client
from .Actions import Actions

windll.shcore.SetProcessDpiAwareness(1) # fix blurry font

class Window:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title("Rock, paper, scissors")
        use_dark_theme()
        
        self.client = self.connect_client()
        self.actions = self.connect_actions()
        
        self.generate_menu_frame()
        self.generate_login_frame()
        self.generate_create_game_frame()
        self.generate_join_game_frame()
        
    def connect_client(self):
        return Client(self)
        
    def connect_actions(self):
        return Actions(self, self.client)
        
    def show_frame(self, frame_to_show: Frame):
        self.current_frame.pack_forget()
        self.current_frame = frame_to_show
        self.current_frame.pack()
        
    def run(self):
        self.current_frame = self.login_main_frame
        self.current_frame.pack()
        self.root.mainloop()

    def generate_login_frame(self):
        self.login_main_frame = Frame(master=self.root)
        self.username = StringVar(master=self.root)
        Label(master=self.login_main_frame, text="Enter username", font=(25)).grid(row=0, column=0, padx=5, pady=100)
        Entry(master=self.login_main_frame, textvariable=self.username, width=50).grid(row=1, column=0, padx=5, pady=10)
        Button(master=self.login_main_frame, text="Log in", command=self.actions.login_action).grid(row=2, column=0, padx=5, pady=10)
        self.login_errors = Text(master=self.login_main_frame, fg="red", state="disabled")
        self.login_errors.grid(row=3, column=0, padx=5, pady=10)
        
    def set_error(self, error: str, error_widget: Text):
        error_widget.config(state="normal")
        error_widget.delete("1.0", END)
        error_widget.insert(INSERT, error)
        error_widget.config(state="disabled")
        
    def generate_menu_frame(self):
        self.menu_main_frame = Frame(master=self.root)
        Button(master=self.menu_main_frame, text="Join game", command=lambda: self.show_frame(self.join_game_main_frame), width=50).grid(row=0, column=0, padx=5, pady=50)
        Button(master=self.menu_main_frame, text="Create game", command=lambda: self.show_frame(self.create_game_main_frame), width=50).grid(row=1, column=0, padx=5, pady=50)
    
    def generate_join_game_frame(self):
        self.join_game_main_frame = Frame(master=self.root)
        # here I need to ask the server for a list of available games
        Button(master=self.join_game_main_frame, text="Cancel", command=lambda: self.show_frame(self.menu_main_frame), width=50).grid(row=0, column=0, padx=5, pady=50)
        
    def generate_create_game_frame(self):
        self.create_game_main_frame = Frame(master=self.root)
        self.game_name = StringVar(master=self.root)
        self.wins_required = StringVar(master=self.root)
        self.password = StringVar(master=self.root)
        Label(master=self.create_game_main_frame, text="Game name", font=(25)).grid(row=0, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.game_name, width=50).grid(row=1, column=0, padx=5, pady=20)
        Label(master=self.create_game_main_frame, text="Required wins", font=(25)).grid(row=2, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.wins_required, width=50).grid(row=3, column=0, padx=5, pady=20)
        Label(master=self.create_game_main_frame, text="Password", font=(25)).grid(row=4, column=0, padx=5, pady=10)
        Entry(master=self.create_game_main_frame, textvariable=self.password, width=50).grid(row=5, column=0, padx=5, pady=20)
        Button(master=self.create_game_main_frame, text="Create Game", command=self.actions.create_game_action).grid(row=6, column=0, padx=5, pady=75)
        Button(master=self.create_game_main_frame, text="Cancel", command=lambda: self.show_frame(self.menu_main_frame), width=50).grid(row=7, column=0, padx=5, pady=50)

    def generate_game_frame(self):
        self.game_main_frame = Frame(master=self.root)
        Label(master=self.game_main_frame, text="You", font=(25)).grid(row=0, column=0, columnspan=2, padx=5, pady=10)
        Label(master=self.game_main_frame, text="Opponent", font=(25)).grid(row=0, column=2, columnspan=2, padx=5, pady=10)

        # here moves will be displayed (text or img)
        Label(master=self.game_main_frame, text="Your move", font=(25)).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        Label(master=self.game_main_frame, text="Opponent's move", font=(25)).grid(row=1, column=2, columnspan=2, padx=5, pady=10)
        
        # button controls
        Button(master=self.game_main_frame, text='Rock', command=lambda: self.actions.make_move_action("rock"), width=33).grid(row=2, column=0, padx=2, pady=5)
        Button(master=self.game_main_frame, text='Paper', command=lambda: self.actions.make_move_action("paper"), width=33).grid(row=2, column=1, columnspan=2, padx=2, pady=5)
        Button(master=self.game_main_frame, text='Scisors', command=lambda: self.actions.make_move_action("scisors"), width=33).grid(row=2, column=3, padx=2, pady=5)

    def show_winner(self):
        winner = Label(master=self.game_main_frame, text="YOU WIN", font=(25))
        winner.place(relx = 0.5, rely = 0.5, anchor = CENTER)
