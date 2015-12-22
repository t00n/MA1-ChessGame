from chess import *


def print_test(paths):
    print(end='  ')
    for a in string.ascii_lowercase[:8]:
        print(a, end=' ')
    print()
    for i in range(7, -1, -1):
        print(i+1, end=' ')
        for j in range(8):
            pos = (j, i)
            ok = False
            if len(paths) > 0:
                if isinstance(paths[0], list):
                    for path in paths:
                        if pos in path:
                            print('x', end=' ')
                            ok = True
                    if not ok:
                        print(' ', end=' ')
                elif isinstance(paths[0], tuple):
                    if pos in paths:
                        print('x', end=' ')
                    else:
                        print(' ', end=' ')
        print()
    print(paths)


def test_path():
    assert diag_paths(0,0) == [[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)], [], [], []]
    assert diag_paths(6,4) == [[(7, 5)], [(7, 3)], [(5, 3), (4, 2), (3, 1), (2, 0)], [(5, 5), (4, 6), (3, 7)]]
    assert diag_paths(4,6) == [[(5, 7)], [(5, 5), (6, 4), (7, 3)], [(3, 5), (2, 4), (1, 3), (0, 2)], [(3, 7)]]
    assert diag_paths(7,7) == [[], [], [(6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1), (0, 0)], []]
    assert diag_paths(7,0) == [[], [], [], [(6, 1), (5, 2), (4, 3), (3, 4), (2, 5), (1, 6), (0, 7)]]
    assert diag_paths(0,7) == [[], [(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)], [], []]
    assert diag_paths(4,4) == [[(5, 5), (6, 6), (7, 7)], [(5, 3), (6, 2), (7, 1)], [(3, 3), (2, 2), (1, 1), (0, 0)], [(3, 5), (2, 6), (1, 7)]]
    assert h_v_paths(0,0) == [[(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)], [], [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)], []]
    assert h_v_paths(0,7) == [[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7)], [], [], [(0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0)]]
    assert h_v_paths(7,0) == [[], [(6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0)], [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)], []]
    assert h_v_paths(7,7) == [[], [(6, 7), (5, 7), (4, 7), (3, 7), (2, 7), (1, 7), (0, 7)], [], [(7, 6), (7, 5), (7, 4), (7, 3), (7, 2), (7, 1), (7, 0)]]
    assert h_v_paths(3,6) == [[(4, 6), (5, 6), (6, 6), (7, 6)], [(2, 6), (1, 6), (0, 6)], [(3, 7)], [(3, 5), (3, 4), (3, 3), (3, 2), (3, 1), (3, 0)]]
    assert h_v_paths(6,2) == [[(7, 2)], [(5, 2), (4, 2), (3, 2), (2, 2), (1, 2), (0, 2)], [(6, 3), (6, 4), (6, 5), (6, 6), (6, 7)], [(6, 1), (6, 0)]]
    assert King(Color.WHITE, (0,0)).paths() == [[(0, 1)], [(1, 0)], [(1, 1)]]
    assert King(Color.WHITE, (7,7)).paths() == [[(6, 6)], [(6, 7)], [(7, 6)]]
    assert King(Color.WHITE, (5,1)).paths() == [[(4, 0)], [(4, 1)], [(4, 2)], [(5, 0)], [(5, 2)], [(6, 0)], [(6, 1)], [(6, 2)]]
    assert Knight(Color.WHITE, (0,0)).paths() == [[(1, 2)], [(2, 1)]]
    assert Knight(Color.WHITE, (5,2)).paths() == [[(3, 1)], [(3, 3)], [(4, 0)], [(4, 4)], [(6, 0)], [(6, 4)], [(7, 1)], [(7, 3)]]
    assert Knight(Color.WHITE, (3,7)).paths() == [[(1, 6)], [(2, 5)], [(4, 5)], [(5, 6)]]
    assert Pawn(Color.WHITE, (6,1)).paths() == [[(6, 2), (6, 3)]]
    assert Pawn(Color.WHITE, (6,2)).paths() == [[(6, 3)]]
    assert Pawn(Color.WHITE, (6,6)).paths() == [[(6, 7)]]
    assert Pawn(Color.WHITE, (6,7)).paths() == []
    assert Pawn(Color.BLACK, (6,6)).paths() == [[(6, 5), (6, 4)]]
    assert Pawn(Color.BLACK, (6,5)).paths() == [[(6, 4)]]
    assert Pawn(Color.BLACK, (6,1)).paths() == [[(6, 0)]]
    assert Pawn(Color.BLACK, (6,0)).paths() == []

def test_board():
    board = Chessboard()
    assert board.compute_moves(board.board[0][5]) == []
    assert board.compute_moves(board.board[1][5]) == [(5, 2), (5, 3)]
    with pytest.raises(Exception):
        board.move((6,6), (6,4))
    board.move((6,1), (6,3))
    with pytest.raises(Exception):
        board.move((6,3), (6,5))
    board.move((1,6), (1,4))
    with pytest.raises(Exception):
        board.move((6,3), (6,5))
