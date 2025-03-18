from chess import Board, Move, square_name, parse_square, square_file, square_rank, SQUARES, KING, ROOK, BISHOP
from copy import deepcopy as copy
from numpy import sign

class Game_state:
    colors = ["Black", "White"]


    def __init__(self):
        self.board = Board()
        self.is_active = False
        self.outcome = None
        self.cannons = {ROOK: [None, None], BISHOP: [None, None]}
        self.is_revealed = {ROOK: [False, False], BISHOP: [False, False]}


    def handle_move_request(self, from_square, to_square, promotion):
        if not self.is_active:
            return
        
        try:
            move, cannon_type, is_capture = self.move_data(from_square, to_square, promotion=promotion)
        except TypeError:
            return 
        
        game_state_copy = copy(self)
        game_state_copy.board.push(move) 
        if game_state_copy.is_in_check(self.board.turn):
            return
        
        to_square_name = square_name(move.to_square)

        if cannon_type:
            self.cannons[cannon_type][self.board.turn] = to_square_name

        for type in ROOK, BISHOP:
            if to_square_name == self.cannons[type][not self.board.turn]:
                self.cannons[type][not self.board.turn] = None

        reveal_cannon = None
        if is_capture:
            for type in ROOK, BISHOP: 
                if self.board.piece_at(parse_square(from_square)).piece_type == type:
                    if not self.is_revealed[type][self.board.turn]: # technically unneeded conditional
                        self.is_revealed[type][self.board.turn] = True
                        reveal_cannon = self.cannons[type][self.board.turn]

        self.board = game_state_copy.board
        self.update_outcome()

        return {"fen": self.board.fen(), "is capture": is_capture, "cannon type": cannon_type, "reveal cannon": reveal_cannon}
 

    def move_data(self, from_square, to_square, promotion=None):
        from_index = parse_square(from_square)
        to_index = parse_square(to_square)

        if self.board.piece_at(to_index) and self.board.piece_at(to_index).piece_type == KING:
            for type in ROOK, BISHOP:
                if self.board.piece_at(from_index).piece_type == type and not self.is_revealed[type][self.board.turn]:
                    return

        target_piece = self.board.piece_at(to_index)
        is_capture = (target_piece and target_piece.color != self.board.turn)

        for type in ROOK, BISHOP:
            if from_square == self.cannons[type][self.board.turn]:
                cannon_type = type
                break
        else:
            cannon_type = None

        move = Move(from_index, to_index, promotion=promotion) 

        if cannon_type and is_capture:
            if not self.is_proper_cannon_capture(from_index, to_index, cannon_type):
                return
        else:
            if move not in self.board.pseudo_legal_moves:
                return

        return (move, cannon_type, is_capture)


    def is_proper_cannon_capture(self, from_index, to_index, cannon_type):
        difference = to_index - from_index 
        step_sign = sign(difference)

        if cannon_type == ROOK:
            if difference % 8 == 0:
                step = 8 * step_sign
            elif to_index // 8 == from_index // 8:
                step = step_sign
            else:
                return False
    
        elif cannon_type == BISHOP:
            if abs(square_file(to_index) - square_file(from_index)) != abs(square_rank(to_index) - square_rank(from_index)):
                return False
            for i in [7, 9]:
                # refactor this to eliminate redundancy with the above?
                if difference % i == 0:
                    step = i * step_sign
                    break
            else:
                return False
            
        path_to_target = list(range(from_index + step, to_index, step))
        pieces_between = [self.board.piece_at(square) for square in path_to_target]

        return (len([piece for piece in pieces_between if piece]) == 1)


    def is_in_check(self, color):
        # Refactor to do swapping before calling the function, depending on context.
        swap = (self.board.turn == color)
        if swap:
            self.board.turn = not self.board.turn

        occupied_squares = (square for square in SQUARES if self.board.piece_at(square))
        enemy_occupied_squares = (square for square in occupied_squares if self.board.piece_at(square).color == self.board.turn)
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
    

    def update_outcome(self):
        result = self.is_checkmate_or_stalemate()
        if result == "checkmate":
            self.outcome = f"{self.colors[not self.board.turn]} wins by checkmate"
            self.is_active = False
        elif result == "stalemate":
            self.outcome = "Draw by stalemate"
            self.is_active = False

    
    def is_checkmate_or_stalemate(self):
        # consider adding occupied squares as a class attribute 
        occupied_squares = (square for square in SQUARES if self.board.piece_at(square))
        self_occupied_squares = (square for square in occupied_squares if self.board.piece_at(square).color == self.board.turn)
        potential_moves = ((square_name(from_square), square_name(to_square)) for from_square in self_occupied_squares for to_square in SQUARES)
        pseudo_legal_moves = [move for move in potential_moves if self.move_data(move[0], move[1])]

        for move in (Move.from_uci(square_pair[0] + square_pair[1]) for square_pair in pseudo_legal_moves):
            game_state_copy = copy(self)
            game_state_copy.board.push(move)
            if not game_state_copy.is_in_check(self.board.turn):
                return False
        
        return "checkmate" if self.is_in_check(self.board.turn) else "stalemate"
