from tkinter import *
from tkinter.ttk import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Window import Window
    from ..game_data import GameData
    from .Actions import Actions

class GameToJoin:

    def __init__(self, window: 'Window', actions: 'Actions', gameData: 'GameData' = {}) -> None:
        self.window = window
        self.gameData = gameData
        self.actions = actions
        #self.generate_game_to_join()
        pass

    def generate_game_to_join(self):
        self.game_item_frame = Frame(master=self.window.join_game_main_frame)
        self.password_input = StringVar(master=self.game_item_frame)
        Label(master=self.game_item_frame, text="self.gameData.game_id", font=(25)).grid(row=0, column=1, padx=5, pady=10)
        Label(master=self.game_item_frame, text="self.gameData.game_owner", font=(25)).grid(row=0, column=2, padx=5, pady=10)
        Label(master=self.game_item_frame, text="self.gameData.wins_required", font=(25)).grid(row=0, column=3, padx=5, pady=10)
        if('self.gameData.password' != ''):
            Entry(master=self.game_item_frame, textvariable=self.password_input, width=50).grid(row=0, column=4, padx=5, pady=20)
            Button(master=self.game_item_frame, text='Join', command=self.join_game).grid(row=0, column=5, padx=2, pady=5)
        else:
            Button(master=self.game_item_frame, text='Join', command=lambda: self.actions.join_game_action).grid(row=0, column=4, padx=2, pady=5)

        #for testing
        self.game_item_frame.grid(row=3, column=0)
        pass

    def join_game(self):
        if self.password_input == self.gameData.password:
            self.actions.join_game_action()
        else:
            error = Label(master=self.game_main_frame, text="incorrect password", font=(25))
            error.place(relx = 0.5, rely = 0.5, anchor = CENTER)
        pass