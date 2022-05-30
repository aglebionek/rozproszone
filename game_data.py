class GameData:
    def __init__(self, game_name = '', player1 = '', player2 = '', wins_required = 1) -> None:
        self.player1 = player1 # set
        self.game_owner = self.player1 # do I need that?
        self.player2 = player2 # set
        self.game_name = game_name # set
        self.wins_required = wins_required # set
        self.player1_wins = 0
        self.player2_wins = 0
        self.player1_choice = ''
        self.player2_choice = '' # meaning they didn't pick anythin, TODO assign values to rock, paper scissors and make a dict that defines who won
        self.winner = ''
        self.password = '' #set
        
    def __str__(self) -> str:
        return f'''
        game_name: {self.game_name}
        wins_required: {self.wins_required}
        password: {self.password}
        player1: {self.player1}
        player1_choice: {self.player1_choice}
        player1_wins: {self.player1_wins}
        player2: {self.player2}
        player2_choice: {self.player2_choice}
        player2_wins: {self.player2_wins}
        winner: {self.winner}
        '''