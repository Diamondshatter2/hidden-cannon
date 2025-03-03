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
        self.status = "inactive"
        self.outcome = None
        self.fen = chess.STARTING_FEN
        self.cannons = {'rook': [None, None], 'bishop': [None, None]}
        self.is_revealed = {'rook': [False, False], 'bishop': [False, False]}


    def make_move(self, move_data):
        if self.status == "inactive":
            return
        
        from_index = chess.parse_square(move_data["from"])
        to_index = chess.parse_square(move_data["to"])

        target_piece = self.board.piece_at(to_index)
        is_capture = (target_piece is not None and target_piece.color != self.board.turn)

        for type in ['rook', 'bishop']:
            if move_data["from"] in self.cannons[type]:
                cannon_type = type
                break
        else:
            cannon_type = None

        if cannon_type == "rook" and is_capture:
            return self.make_rook_cannon_move(move_data)
        
        if cannon_type == "bishop" and is_capture:
            return self.make_bishop_cannon_move(move_data)

        move = chess.Move(from_index, to_index) 
        if move in self.board.pseudo_legal_moves:  
            return self.push_move(move, cannon_type, is_capture=is_capture)
        

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

        if len([piece for piece in pieces_between if piece is not None]) == 1:
            move = chess.Move(from_index, to_index)
            return self.push_move(move, "rook", is_capture=True)


    def make_bishop_cannon_move(self, move_data):
        from_index = chess.parse_square(move_data["from"])
        to_index = chess.parse_square(move_data["to"])
        difference = to_index - from_index 

        for i in [7, 9]:
            if difference % i == 0:
                step = i * sign(difference)
                break
        else:
            return
        
        path_to_target = list(range(from_index + step, to_index, step))
        pieces_between = [self.board.piece_at(square) for square in path_to_target]

        if len([piece for piece in pieces_between if piece is not None]) == 1:
            move = chess.Move(from_index, to_index)
            return self.push_move(move, "bishop", is_capture=True)
        

    def push_move(self, move, cannon_type, is_capture="false"):
        self.board.push(move) 
        self.fen = self.board.fen()

        if cannon_type:
            self.cannons[cannon_type][self.whose_turn] = chess.square_name(move.to_square) # refactor cannons to use indices

        self.whose_turn = 1 - self.whose_turn # Toggle between 0 and 1

        for type in ['rook', 'bishop']:
            if chess.square_name(move.to_square) == self.cannons[type][self.whose_turn]:
                self.cannons[type][self.whose_turn] = None

        print(self.cannons)
    
        return {"fen": self.fen, "is capture": is_capture, "cannon type": cannon_type}
