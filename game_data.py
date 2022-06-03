class GameData:
    def __init__(self, game_name = '', player1 = '', player2 = '', wins_required = 1) -> None:
        self.player1 = player1 
        self.game_owner = self.player1 
        self.player2 = player2 
        self.game_name = game_name 
        self.wins_required = wins_required 
        self.player1_wins = 0
        self.player2_wins = 0
        self.player1_choice = ''
        self.player2_choice = ''
        self.winner = ''
        self.password = '' 
        
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