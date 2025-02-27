import chess


class Game:
    colors = ["White", "Black"]
    
    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.players = [None, None]
        self.usernames = [None, None]
        self.messages = []
        self.board = chess.Board()
        self.whose_turn = 0
        self.outcome = None
        self.fen = chess.STARTING_FEN
        self.cannons = {'rook': [None, None], 'bishop': [None, None]}

    def make_move(self, move_data):
        if move_data["from"] in self.cannons['rook']:
            return self.make_rook_cannon_move(move_data)
        
        if move_data["from"] in self.cannons['bishop']:
            return self.make_bishop_cannon_move(move_data)
        
        move = chess.Move.from_uci(move_data["from"] + move_data["to"]) 

        if self.outcome is None and move in self.board.legal_moves:  
            move_type = "capture" if self.board.is_capture(move) else "normal"
            self.board.push(move) 
            self.fen = self.board.fen()
            self.whose_turn = 1 - self.whose_turn # Toggle between 0 and 1
            return move_type, self.fen
        
    
    def make_rook_cannon_move(self, move_data):
        if not (move_data["from"][0] == move_data["to"][0] or move_data["from"][1] == move_data["to"][1]):
            return
        

    def make_bishop_cannon_move(self, move_data):
        pass
