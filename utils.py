#!/usr/bin/env python

"""
utils.py - This file contains the definition of
the function essential for the good work of the API.
"""

import json
import os
import time
import uuid

from random import randint, shuffle
from copy import deepcopy

from google.appengine.api import urlfetch

from game_model import Game


def getUserId(user, id_type="email"):
    if id_type == "email":
        return user.email()

    if id_type == "oauth":
        """A workaround implementation for getting userid."""
        auth = os.getenv('HTTP_AUTHORIZATION')
        bearer, token = auth.split()
        token_type = 'id_token'
        if 'OAUTH_USER_ID' in os.environ:
            token_type = 'access_token'
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?%s=%s'
               % (token_type, token))
        user = {}
        wait = 1
        for i in range(3):
            resp = urlfetch.fetch(url)
            if resp.status_code == 200:
                user = json.loads(resp.content)
                break
            elif resp.status_code == 400 and 'invalid_token' in resp.content:
                url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?%s=%s'
                       % ('access_token', token))
            else:
                time.sleep(wait)
                wait = wait + i
        return user.get('user_id', '')

    if id_type == "custom":
        # implement your own user_id creation and getting algorythm
        # this is just a sample that queries datastore for an existing profile
        # and generates an id if profile does not exist for an email
        profile = Game.query(Game.mainEmail == user.email())
        if profile:
            return profile.id()
        else:
            return str(uuid.uuid1().get_hex())


def shipsCoordinates(board_setup, board_size=10):
    """Main function to generate the board"""
    board = []
    ships = []
    rand_dir = []
    rand_dir.append([0, 1])
    rand_dir.append([1, 0])
    rand_dir.append([-1, 0])
    rand_dir.append([0, -1])

    for x in range(board_size):
        board.append(["0"] * board_size)

    def random_row(board):
        return randint(0, len(board) - 1)

    def random_col(board):
        return randint(0, len(board[0]) - 1)

    def test(liste, z):
        if sum([1 for piece in liste[-z:] if piece[0] ==
                liste[-z][0] or piece[1] == liste[-z][1]]) < z:
            return True
        else:
            return False

    def posShip(x, y, ship, z, boardI):
        """Flood fill like function to place the ship on the board."""
        try:
            if not int(boardI[x][y])and x >= 0 and y >= 0:
                if test(ship, z):
                    boardI[x][y] = "1"
                    ship.append([x, y])
                    posShip(
                        x + rand_dir[0][0],
                        y + rand_dir[0][1],
                        ship,
                        z,
                        boardI)
                    posShip(
                        x + rand_dir[1][0],
                        y + rand_dir[1][1],
                        ship,
                        z,
                        boardI)
                    posShip(
                        x + rand_dir[2][0],
                        y + rand_dir[2][1],
                        ship,
                        z,
                        boardI)
                    posShip(
                        x + rand_dir[3][0],
                        y + rand_dir[3][1],
                        ship,
                        z,
                        boardI)
                else:
                    return ship[-z:]
            else:
                return False
        except IndexError:
            return
        return ship[-z:]

    def createShip(z):
        """Specifying first the lenght of the boat,
        this function creating it in the space of the board"""
        ship = False

        # rand_dir is a list defining the way in which
        # the flood fill is processing (right, bottom, left, top, or
        # left, right, bottom, top or any other combination)
        # this is to prevent the boats to always have
        # the same orientation on the map
        shuffle(rand_dir)

        while ship is False:
            ship_row = random_row(board)
            ship_col = random_col(board)
            ship2 = [(-nombre - 10, -nombre - 10) for nombre in range(z)]
            boardI = deepcopy(board)

            ship = posShip(ship_row, ship_col, ship2, z, boardI)

        for piece in ship:
            board[piece[0]][piece[1]] = "1"
            ships.append(piece[0])
            ships.append(piece[1])

    for boat in board_setup:
        createShip(boat)

    return ships
