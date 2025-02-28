import chess
from numpy import sign


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
        to_index = chess.parse_square(move_data["to"])

        if move_data["from"] in self.cannons['rook'] and self.board.piece_at(to_index) is not None:
            return self.make_rook_cannon_move(move_data)
        
        if move_data["from"] in self.cannons['bishop'] and self.board.piece_at(to_index) is not None:
            return self.make_bishop_cannon_move(move_data)
        
        move = chess.Move.from_uci(move_data["from"] + move_data["to"]) 

        if self.outcome is None and move in self.board.legal_moves:  
            move_type = "capture" if self.board.is_capture(move) else "normal"
            self.board.push(move) 
            self.fen = self.board.fen()

            for type in ['rook', 'bishop']:
                if move_data["from"] in self.cannons[type]: # second time checking for this, obviously needs refactoring
                    self.cannons[type][self.whose_turn] = move_data["to"]

            self.whose_turn = 1 - self.whose_turn # Toggle between 0 and 1
            return move_type, self.fen
        
    
    def make_rook_cannon_move(self, move_data):
        if move_data["from"][0] == move_data["to"][0] and move_data["from"][1] != move_data["to"][1]:
            abs_step = 8
        elif move_data["from"][1] == move_data["to"][1] and move_data["from"][0] != move_data["to"][0]:
            abs_step = 1
        else:
            return

        
        from_index = chess.parse_square(move_data["from"])
        to_index = chess.parse_square(move_data["to"])
        step = abs_step * sign(to_index - from_index)
        path_to_target = list(range(from_index + step, to_index, step))
        pieces_between = [self.board.piece_at(square) for square in path_to_target]
        print(path_to_target)
        print(pieces_between, "\n\n\n")

        


        

    def make_bishop_cannon_move(self, move_data):
        print("bishop cannon move attemped")
