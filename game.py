class Game:
    colors = ['red', 'yellow']
    spaces = {(column, row) for column in range(7) for row in range(6)}
    vectors = ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1))

    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.players = [None, None]
        self.usernames = [None, None]
        self.messages = []
        self.board = [[None for row in range(6)] for column in range(7)]
        self.whose_turn = 0
        self.outcome = None

    
    def make_move(self, column):
        if self.outcome is not None or not 0 <= column < 7:
            return 
        
        row = sum(space is not None for space in self.board[column])
        if row >= 6:
            return 
        
        self.board[column][row] = self.whose_turn
        self.outcome = self.determine_outcome((column, row))
        move_data = {"column": column, "row": row, "player": self.whose_turn}
        self.whose_turn = int(not self.whose_turn)

        return move_data

    
    def determine_outcome(self, space):
        for direction in range(4):
            if self.consecutive_tokens(space, direction) + self.consecutive_tokens(space, direction + 4) >= 3:
                return self.board[space[0]][space[1]]
        
        if all(all(space != None for space in column) for column in self.board):
            return "draw"
        
        
    def consecutive_tokens(self, space, direction):
        vector = Game.vectors[direction]
        next_space = space[0] + vector[0], space[1] + vector[1]

        if next_space not in Game.spaces or self.board[next_space[0]][next_space[1]] != self.board[space[0]][space[1]]:
            return 0
        
        return 1 + self.consecutive_tokens(next_space, direction)
