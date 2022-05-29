class GameData:
    def __init__(self, game_name = '', player1 = '', player2 = '', wins_required = 1) -> None:
        self.player1 = player1
        self.game_owner = self.player1
        self.player2 = player2
        self.game_name = game_name
        self.wins_required = wins_required
        self.player1_wins = 0
        self.player2_wins = 0
        self.player1_choice = 0
        self.player2_choice = 0 # meaning they didn't pick anythin, TODO assign values to rock, paper scissors and make a dict that defines who won
        self.winner = ''
        self.password = '' #?