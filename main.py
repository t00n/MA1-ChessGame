from chess import Chessboard
from graphics import Window
from dataloader import geometries
from PyQt4.QtGui import QApplication
import sys

if __name__ == '__main__':
    board = Chessboard()
    app = QApplication(sys.argv)
    window = Window(geometries, board)
    window.show()
    sys.exit(app.exec_())
