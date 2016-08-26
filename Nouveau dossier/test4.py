def posBoat(x, y, ship, z, board):

    try:
        if not int(boardI[x][y]):
            boardI[x].pop(y)
            boardI[x].insert(y, "1")
            if test(ship, z):
                ship.append([x, y])
                posBoat(x, y+1, ship, z, boardI)
                posBoat(x+1, y, ship, z, boardI)
                posBoat(x, y-1, ship, z, boardI)
                posBoat(x-1, y, ship, z, boardI)
            else:
                return
        else:
            return
    except IndexError:
        return
    except UnboundLocalError:
        boardI = list(board)
        posBoat(x, y, ship, z, boardI)
    return ship[-z:]