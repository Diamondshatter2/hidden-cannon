import chess


class Game:
    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.players = [None, None]
        self.usernames = [None, None]
        self.messages = []
        self.board = chess.Board()
        self.whose_turn = 0
        self.outcome = None

    def make_move(self, move_data):
        move = chess.Move.from_uci(move_data["from"] + move_data["to"]) 

        if move in self.board.legal_moves:  
            self.board.push(move) 
            return self.board.fen()