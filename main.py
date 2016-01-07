#!/usr/bin/env python3
from chess import Chessboard
from gui import Window
from gl_data import geometries
from PyQt4.QtGui import QApplication
import sys

if __name__ == '__main__':
    board = Chessboard()
    app = QApplication(sys.argv)
    window = Window(geometries, board)
    window.show()
    sys.exit(app.exec_())
