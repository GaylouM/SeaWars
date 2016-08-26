board = [5]

boardI = list(board)

print id(boardI)
print id(board)

print boardI
print board

boardI.append(1)

print id(boardI)
print id(board)

print boardI
print board

def test(boardJ):
    boardJ.append(1)

boardJ = list(board)

print id(boardJ)
print id(board)

print boardJ
print board

test(boardJ)

print id(boardJ)
print id(board)

print boardJ
print board
