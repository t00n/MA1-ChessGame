from chess import Chessboard
from graphics import Window
from dataloader import geometries


if __name__ == '__main__':
    board = Chessboard()
    window = Window(geometries, board)
