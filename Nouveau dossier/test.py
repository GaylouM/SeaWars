from random import randint

board = []

for x in range(0, 10):
    board.append(["O"] * 10)

def print_board(board):
    for row in board:
        print " ".join(row)

print_board(board)

def random_row(board):
    return randint(0, len(board) - 1)

def random_col(board):
    return randint(0, len(board[0]) - 1)

ship_row = random_row(board)
ship_col = random_col(board)
guess_row = int(raw_input("Guess Row:"))
guess_col = int(raw_input("Guess Col:"))

print ship_row
print ship_col

# Write your code below!
if guess_col == ship_col and guess_row == ship_row:
    print "Congratulations! You sank my battleship!"
else:
    print "You missed my battleship!"
    try:
        if board[guess_row][guess_col] == "X":
            print "This place was already shot"
        else:
            board[guess_row][guess_col] = "X"
            print_board(board)
    except IndexError:
        print "Oops, that's not even in the ocean."
