class GameData:
    def __init__(self, player1 = '', player2 = '', wins_required = 1) -> None:
        self.player1 = player1
        self.player2 = player2
        self.wins_required = wins_required
        self.player1_wins = 0
        self.player2_wins = 0
        self.winner = ''
        self.password = '' #?