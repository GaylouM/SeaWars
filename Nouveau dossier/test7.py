##board = []
##
##for x in range(0, 10):
##    board.append(["0"] * 10)
##
##def print_board(liste):
##    for row in liste:
##        print " ".join(row)
##
##boardI = list(board)
##
##def posBoat(boardI):
##
##    for x in range(5):
##        boardI[x][x] = "1"
##        print_board(board)
##
##posBoat(boardI)

from copy import deepcopy

board = []

board.append(["0"] * 10)

##def print_board(liste):
##    for row in liste:
##        print " ".join(row)

boardI = list(board)
boardI[0].append("1")
print boardI is board
print board
print boardI

##def posBoat(boardI):
##
##    boardI[0].append("1")
##    print_board(board)
##
##posBoat(boardI)
