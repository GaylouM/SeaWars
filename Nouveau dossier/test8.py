##board = []
##
##for x in range(0, 10):
##    board.append(['0'] * 10)
##    
##def print_board(liste):
##    for row in liste:
##        print (" ".join(row))
##
##boardI = list(board)
##
##def posBoat(boardI):
##
##    for x in range(5):
##        boardI[x][x] = '1'
##        print_board(board)
##
##posBoat(boardI)

board = []

for x in range(0, 10):
    board.append(['0'] * 10)
    
def print_board(liste):
    for row in liste:
        print (" ".join(row))

boardI = list(board)

def posBoat(boardI):

    boardI[1].append(1)
    boardI[0].pop()
    print_board(board)

posBoat(boardI)
