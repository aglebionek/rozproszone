from tkinter import *
from tkinter.ttk import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Window import Window
    from game_data import GameData
    from .Actions import Actions

class GameToJoin:

    def __init__(self, window: 'Window', actions: 'Actions',  game_data: 'GameData' = {}) -> None:
        self.window = window
        self.game_data = game_data
        self.actions = actions
        pass

    def generate_game_to_join(self, row):
        self.game_item_frame = Frame(master=self.window.join_game_main_frame)
        self.password_input = StringVar(master=self.game_item_frame, value='')
        Label(master=self.game_item_frame, text=f"game name: {self.game_data.game_name}", font=(25)).grid(row=0, column=1, padx=5, pady=10)
        Label(master=self.game_item_frame, text=f"owner: {self.game_data.game_owner}", font=(25)).grid(row=0, column=2, padx=5, pady=10)
        Label(master=self.game_item_frame, text=f"wins required: {self.game_data.wins_required}", font=(25)).grid(row=0, column=3, padx=5, pady=10)
        state='disabled'
        if(self.game_data.password != ''): state='normal'
        Entry(master=self.game_item_frame, textvariable=self.password_input, width=50, state=state).grid(row=0, column=4, padx=5, pady=20)
        Button(master=self.game_item_frame, text='Join', command= self.join_game).grid(row=0, column=5, padx=2, pady=5)
        self.join_error = Text(master=self.game_item_frame, fg="red", state="disabled", borderwidth=0, height=1)
        self.join_error.bindtags((str(self.join_error), str(self.window.root), "all"))
        self.join_error.grid(row=1, column=0, pady=5, columnspan=5)    

        self.game_item_frame.grid(row=row, column=0)

    def join_game(self):
        if self.password_input.get() == self.game_data.password:
            self.actions.join_game(game_name=self.game_data.game_name)
        else:
            self.window.set_error("Incorrect password", self.join_error)
        pass