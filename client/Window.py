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
        self.actions = self.connect_action()
        
        self.generate_menu_frame()
        self.generate_login_frame()
        self.game_frame = Frame(master=self.root)
        self.join_game_frame = Frame(master=self.root)     
        
    def connect_client(self):
        return Client(self)
        
    def connect_action(self):
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
        Button(master=self.login_main_frame, text="Zaloguj", command=self.actions.login_action).grid(row=2, column=0, padx=5, pady=10)
        self.login_errors = Text(master=self.login_main_frame, fg="red", state="disabled")
        self.login_errors.grid(row=3, column=0, padx=5, pady=10)
        
    def set_login_error(self, error):
        self.login_errors.config(state="normal")
        self.login_errors.delete("1.0", END)
        self.login_errors.insert(INSERT, error)
        self.login_errors.config(state="disabled")
        
    def generate_menu_frame(self):
        self.menu_main_frame = Frame(master=self.root)
        Button(master=self.menu_main_frame, text="Join game", command=lambda: self.actions.join_game, width=50).grid(row=0, column=0, padx=5, pady=50)
        Button(master=self.menu_main_frame, text="Create grę", command=lambda: self.actions.create_game, width=50).grid(row=1, column=0, padx=5, pady=50)
    
    def generate_join_game_frame(self):
        pass

