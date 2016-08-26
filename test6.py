from random import randint, shuffle
from collections import deque
from copy import deepcopy

board = []
ships = []
rand_dir = []
rand_dir.append([0,1])
rand_dir.append([1,0])
rand_dir.append([-1,0])
rand_dir.append([0,-1])

for x in range(0, 10):
    board.append(["0"] * 10)

def print_board(board):
    for row in board:
        print " ".join(row)

def random_row(board):
    return randint(0, len(board) - 1)

def random_col(board):
    return randint(0, len(board[0]) - 1)

def test(liste, z):
	if sum([1 for piece in liste[-z:] if piece[0] == liste[-z][0] or piece[1] == liste[-z][1]]) < z:
		return True
	else:
		return False

def posShip(x, y, ship, z, boardI):

    try:
        if not int(boardI[x][y])and x >= 0 and y >= 0:
            if test(ship, z):
                boardI[x][y] = "1"
                ship.append([x, y])
                posShip(x+rand_dir[0][0], y+rand_dir[0][1], ship, z, boardI)
                posShip(x+rand_dir[1][0], y+rand_dir[1][1], ship, z, boardI)
                posShip(x+rand_dir[2][0], y+rand_dir[2][1], ship, z, boardI)
                posShip(x+rand_dir[3][0], y+rand_dir[3][1], ship, z, boardI)
            else:
                return ship[-z:]
        else:
            return False
    except IndexError:
        return
    return ship[-z:]

def createShip(z):

    ship = False

    shuffle(rand_dir)

    while ship is False:
        ship_row = random_row(board)
        ship_col = random_col(board)
        ship2 = [(-nombre-10, -nombre-10) for nombre in range(z)]
        boardI = deepcopy(board)

        ship = posShip(ship_row, ship_col, ship2, z, boardI)

    ships.append(ship)
    for piece in ship:
        board[piece[0]][piece[1]] = "1"
    print_board(board)
    print "%s" %ship
    print "\n"

createShip(5)
createShip(4)
createShip(3)
createShip(3)
createShip(2)

