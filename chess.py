from abc import ABCMeta, abstractmethod
import pytest
import string
import math

class Color:
    WHITE=0
    BLACK=1

    @staticmethod
    def invert(color):
        if color == Color.BLACK:
            return Color.WHITE
        return Color.BLACK

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

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]

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

    @property
    def next(self):
        if self.color == Color.WHITE:
            return self.y+1
        else:
            return self.y-1

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
        self.history = []

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

    def __iter__(self):
        for i in range(8):
            for j in range(8):
                if self.board[j][i] != None:
                    yield self.board[j][i]

    def king_in_check(self, color):
        for i in range(8):
            for j in range(8):
                chessman = self.board[j][i]
                if isinstance(chessman, King) and chessman.color == color:
                    king = chessman
        for i in range(8):
            for j in range(8):
                chessman = self.board[j][i]
                if chessman != None and chessman.color != color and king.position in self.compute_moves(chessman):
                    return True
        return False

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
                if cellman != None:
                    break
        # pawn capture
        if isinstance(chessman, Pawn):
            captures = [(i,chessman.next) for i in [chessman.x-1, chessman.x+1] if i >= 0 and i < 8 and chessman.next >= 0 and chessman.next < 8 and self.board[chessman.next][i] != None and self.board[chessman.next][i].color != chessman.color]
            moves.extend(captures)
        return moves

    def legal_moves(self, chessman):
        moves = self.compute_moves(chessman)
        newmoves = []
        for move in moves:
            self.do(chessman.position, move)
            if not self.king_in_check(chessman.color):
                newmoves.append(move)
            self.revert()
        return newmoves

    def move(self, fr, to):
        chessman = self.select(fr)
        if to in self.legal_moves(chessman):
            self.do(fr, to)
            self.turn = Color.invert(self.turn)
        else:
            raise Exception('Can\'t go there !')

    def do(self, fr, to):
        self.history.append({
            'fr': {
                'index': fr, 
                'cell': self.board[fr[1]][fr[0]]
                },
            'to': {
                'index': to,
                'cell': self.board[to[1]][to[0]]
            }})
        self.board[to[1]][to[0]] = self.board[fr[1]][fr[0]]
        self.board[to[1]][to[0]].move(to)
        self.board[fr[1]][fr[0]] = None

    def revert(self, n=1):
        for i in range(n):
            move = self.history.pop()
            fr = move['fr']
            to = move['to']
            self.board[fr['index'][1]][fr['index'][0]] = fr['cell']
            self.board[fr['index'][1]][fr['index'][0]].move(fr['index'])
            self.board[to['index'][1]][to['index'][0]] = to['cell']