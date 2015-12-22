from chess import Chessboard, King, Queen, Rook, Bishop, Knight, Pawn, Color

if __name__ == '__main__':
    chessboard = Chessboard()
    print(chessboard)
    chessboard.move((6,1), (6,3))
    print(chessboard)
    chessboard.move((1,6), (1,4))