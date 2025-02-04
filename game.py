SPACES = {(column, row) for column in range(7) for row in range(6)}
VECTORS = ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1))


class Game:
    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.players = [None, None]
        self.usernames = [None, None]
        self.messages = []
        self.board = [[None for row in range(6)] for column in range(7)]
        self.whose_turn = 0
        self.outcome = None


def outcome(board, space):
    for direction in range(4):
        if consecutive_tokens(board, space, direction) + consecutive_tokens(board, space, direction + 4) >= 3:
            return board[space[0]][space[1]]
        
    if all(all(space != None for space in column) for column in board):
        return "draw"
    

def consecutive_tokens(board, space, direction):
    vector = VECTORS[direction]
    next_space = space[0] + vector[0], space[1] + vector[1]

    if next_space not in SPACES or board[next_space[0]][next_space[1]] != board[space[0]][space[1]]:
        return 0
    
    return 1 + consecutive_tokens(board, next_space, direction)

