from chess import Board, Move, square_name, parse_square, SQUARES, KING, ROOK, BISHOP
from copy import deepcopy as copy
from numpy import sign

class Game_state:
    colors = ["Black", "White"]


    def __init__(self):
        self.board = Board()
        self.is_active = False
        self.outcome = None
        self.cannons = {"rook": [None, None], "bishop": [None, None]}
        self.is_revealed = {"rook": [False, False], "bishop": [False, False]}


    def handle_move_request(self, from_square, to_square):
        if not self.is_active:
            return
        
        try:
            move, cannon_type, is_capture = self.move_data(from_square, to_square)
        except TypeError:
            return 
        
        game_state_copy = copy(self)
        game_state_copy.board.push(move) 
        if game_state_copy.is_in_check(self.board.turn):
            return
        
        to_square_name = square_name(move.to_square)

        if cannon_type:
            self.cannons[cannon_type][self.board.turn] = to_square_name

        if is_capture:
            for type in [(ROOK, "rook"), (BISHOP, "bishop")]: # refactor this, it's ugly
                if self.board.piece_at(parse_square(from_square)).piece_type == type[0]:
                    if not self.is_revealed[type[1]][self.board.turn]: # technically unneeded conditional
                        self.is_revealed[type[1]][self.board.turn] = True
        
        for type in ["rook", "bishop"]:
            if to_square_name == self.cannons[type][not self.board.turn]:
                self.cannons[type][not self.board.turn] = None

        self.board = game_state_copy.board

        return {"fen": self.board.fen(), "is capture": is_capture, "cannon type": cannon_type}
 

    def move_data(self, from_square, to_square):
        from_index = parse_square(from_square)
        to_index = parse_square(to_square)

        target_piece = self.board.piece_at(to_index)
        is_capture = (target_piece and target_piece.color != self.board.turn)

        for type in ["rook", "bishop"]:
            if from_square == self.cannons[type][self.board.turn]:
                cannon_type = type
                break
        else:
            cannon_type = None

        move = Move(from_index, to_index) 

        if cannon_type and is_capture:
            if not self.is_proper_cannon_capture(from_index, to_index, cannon_type):
                return
        else:
            if move not in self.board.pseudo_legal_moves:
                return

        return (move, cannon_type, is_capture)


    def is_proper_cannon_capture(self, from_index, to_index, cannon_type):
        if self.board.piece_at(to_index).piece_type == KING and not self.is_revealed[cannon_type][self.board.turn]:
            return False

        difference = to_index - from_index 
        step_sign = sign(difference)

        if cannon_type == "rook":
            if difference % 8 == 0:
                step = 8 * step_sign
            elif to_index // 8 == from_index // 8:
                step = step_sign
            else:
                return False
    
        elif cannon_type == "bishop":
            for i in [7, 9]:
                if difference % i == 0:
                    step = i * step_sign
                    break
            else:
                return False
            
        path_to_target = list(range(from_index + step, to_index, step))
        pieces_between = [self.board.piece_at(square) for square in path_to_target]

        return (len([piece for piece in pieces_between if piece]) == 1)


    def is_in_check(self, color):
        swap = (self.board.turn == color)
        if swap:
            self.board.turn = not self.board.turn

        occupied_squares = [square for square in SQUARES if self.board.piece_at(square)]
        enemy_occupied_squares = [square for square in occupied_squares if self.board.piece_at(square).color == self.board.turn]
        king_square = square_name(self.board.king(color))

        for square_index in enemy_occupied_squares:
            origin_square = square_name(square_index)
            if self.move_data(origin_square, king_square):
                check = True
                break
        else:
            check = False
                
        if swap:
            self.board.turn = not self.board.turn
        
        return check

