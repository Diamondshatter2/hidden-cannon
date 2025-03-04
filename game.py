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
        self.cannons = { 'rook': [None, None], 'bishop': [None, None] }
        self.is_revealed = { 'rook': [False, False], 'bishop': [False, False] }


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

        if cannon_type and is_capture:
            return self.make_cannon_move(from_index, to_index, cannon_type)

        move = chess.Move(from_index, to_index) 
        if move in self.board.pseudo_legal_moves:  
            return self.push_move(move, cannon_type, is_capture=is_capture)
    

    def make_cannon_move(self, from_index, to_index, cannon_type):
        difference = to_index - from_index 
        step_sign = sign(difference)

        if cannon_type == "rook":
            if difference % 8 == 0:
                step = 8 * step_sign
            elif to_index // 8 == from_index // 8:
                step = step_sign
            else:
                return
    
        elif cannon_type == "bishop":
            for i in [7, 9]:
                if difference % i == 0:
                    step = i * step_sign
                    break
            else:
                return
            
        path_to_target = list(range(from_index + step, to_index, step))
        pieces_between = [self.board.piece_at(square) for square in path_to_target]

        if len([piece for piece in pieces_between if piece is not None]) == 1:
            move = chess.Move(from_index, to_index)
            return self.push_move(move, cannon_type, is_capture=True)
        

    def push_move(self, move, cannon_type, is_capture="false"):
        board_copy = self.board.copy()
        board_copy.push(move)
        board_copy_fen = board_copy.fen()
        opponent = 1 - self.whose_turn

        if self.is_check(board_copy_fen, opponent):
            return

        self.board = board_copy
        self.fen = board_copy_fen

        if cannon_type:
            self.cannons[cannon_type][self.whose_turn] = chess.square_name(move.to_square) # refactor cannons to use indices

        self.whose_turn = opponent

        for type in ['rook', 'bishop']:
            if chess.square_name(move.to_square) == self.cannons[type][self.whose_turn]:
                self.cannons[type][self.whose_turn] = None

        print(self.cannons)
    
        return {"fen": self.fen, "is capture": is_capture, "cannon type": cannon_type, "is-mate": self.is_checkmate()}
    

    def is_check(self, fen, color): # does this need to be a class method?
        return False # placeholder
    

    def is_checkmate(self):
        if not self.is_check(self.fen, self.whose_turn):
            return
        
        # see if every move is check
