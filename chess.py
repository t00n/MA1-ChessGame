from abc import ABCMeta, abstractmethod
import pytest
import string
import math

class Color:
    WHITE=0
    BLACK=1

def h_v_paths(x, y):
    res = []
    # right
    res.append([(i, y) for i in range(x+1, 8)])
    # left
    res.append([(i, y) for i in range(x-1, -1, -1)])
    # up
    res.append([(x, j) for j in range(y+1, 8)])
    # down
    res.append([(x, j) for j in range(y-1, -1, -1)])
    return res

def diag_paths(x, y):
    res = []
    # right and up
    res.append([(x+i, y+i) for i in range(1, min(8-x, 8-y))])
    # right and down
    res.append([(x+i, y-i) for i in range(1, min(8-x, y+1))])
    # left and down
    res.append([(x-i, y-i) for i in range(1, min(x+1, y+1))])
    # left and up
    res.append([(x-i, y+i) for i in range(1, min(x+1, 8-y))])
    return res

class Chessman:
    __metaclass__ = ABCMeta

    def __init__(self, color, position):
        self.color = color
        self.position = position

    @abstractmethod
    def paths(self):
        pass

    @abstractmethod
    def __str__(self):
        return '\033[97m%s\033[0m' if self.color == Color.WHITE else '\033[90m%s\033[0m'

    def move(self, to):
        self.position = to

class King(Chessman):
    def paths(self):
        x, y = self.position[0], self.position[1]
        res = []
        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                if (i,j) != (x, y) and i >= 0 and i < 8 and j >= 0 and j < 8:
                    res.append([(i,j)])
        return res

    def __str__(self):
        return super(King, self).__str__() % 'K'

class Queen(Chessman):
    def paths(self):
        x, y = self.position[0], self.position[1]
        res = []
        res.extend(h_v_paths(x,y))
        res.extend(diag_paths(x,y))
        return res

    def __str__(self):
        return super(Queen, self).__str__() % 'Q'

class Rook(Chessman):
    def paths(self):
        x, y = self.position[0], self.position[1]
        return h_v_paths(x,y)

    def __str__(self):
        return super(Rook, self).__str__() % 'R'

class Bishop(Chessman):
    def paths(self):
        x, y = self.position[0], self.position[1]
        return diag_paths(x,y)

    def __str__(self):
        return super(Bishop, self).__str__() % 'B'

class Knight(Chessman):
    def paths(self):
        x, y = self.position[0], self.position[1]
        return [[(i,j)] for i in range(x-2, x+3) for j in range(y-2, y+3) if i >= 0 and i < 8 and j >= 0 and j < 8 and ((math.fabs(x-i) == 2 and math.fabs(y-j) == 1) or (math.fabs(x-i) == 1 and math.fabs(y-j) == 2))]

    def __str__(self):
        return super(Knight, self).__str__() % 'N'

class Pawn(Chessman):
    def paths(self):
        x, y = self.position[0], self.position[1]
        res = []
        if self.color == Color.WHITE:
            if y == 1:
                res.append([(x, y+1), (x, y+2)])
            elif y < 7:
                res.append([(x, y+1)])
        elif self.color == Color.BLACK:
            if y == 6:
                res.append([(x, y-1), (x, y-2)])
            elif y > 0:
                res.append([(x, y-1)])
        return res

    def __str__(self):
        return super(Pawn, self).__str__() % 'P'

class Chessboard:
    def __init__(self):
        self.board = [
            [Rook(Color.WHITE, (0,0)), Knight(Color.WHITE, (1,0)), Bishop(Color.WHITE, (2,0)), Queen(Color.WHITE, (3,0)), King(Color.WHITE, (4,0)), Bishop(Color.WHITE, (5,0)), Knight(Color.WHITE, (6,0)), Rook(Color.WHITE, (7,0))],
            [Pawn(Color.WHITE, (i, 1)) for i in range(8)],
            [None for i in range(8)],
            [None for i in range(8)],
            [None for i in range(8)],
            [None for i in range(8)],
            [Pawn(Color.BLACK, (i, 6)) for i in range(8)],
            [Rook(Color.BLACK, (0,7)), Knight(Color.BLACK, (1,7)), Bishop(Color.BLACK, (2,7)), Queen(Color.BLACK, (3,7)), King(Color.BLACK, (4,7)), Bishop(Color.BLACK, (5,7)), Knight(Color.BLACK, (6,7)), Rook(Color.BLACK, (7,7))]            
        ]
        self.turn = Color.WHITE

    def __str__(self):
        res = '  ' + ' '.join(map(str, range(8))) + '\n'
        for i in range(7, -1, -1):
            res += str(i)
            for j in range(8):
                if self.board[i][j] == None:
                    res += '  '
                else:
                    res += ' ' + str(self.board[i][j])
            res += '\n'
        return res

    def select(self, fr):
        chessman = self.board[fr[1]][fr[0]]
        if chessman == None:
            raise Exception('Nothing here')
        if chessman.color != self.turn:
            raise Exception('Not your turn !')
        return chessman

    def compute_moves(self, chessman):
        paths = chessman.paths()
        moves = []
        for path in paths:
            for cell in path:
                cellman = self.board[cell[1]][cell[0]]
                if cellman == None or cellman.color != chessman.color:
                    moves.append(cell)
                else:
                    break
        return moves


    def move(self, fr, to):
        chessman = self.select(fr)
        if to in self.compute_moves(chessman):
            chessman.move(to)
            self.board[to[1]][to[0]] = chessman
            self.board[fr[1]][fr[0]] = None
            if self.turn == Color.WHITE:
                self.turn = Color.BLACK
            else:
                self.turn = Color.WHITE
        else:
            raise Exception('Can\'t go there !')