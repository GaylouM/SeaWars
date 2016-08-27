#!/usr/bin/env python

"""
seawars_api.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game').
"""

import endpoints

from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from exceptions_model import ConflictException

from boolean_model import BooleanMessage

from random import choice

from operator import truediv

from settings import WEB_CLIENT_ID

from protorpc import (
    messages,
    message_types,
    remote,
)

from user_model import (
    Profile,
    ProfileMiniForm,
    ProfileForm,
)

from game_model import (
    Game,
    GameForm,
    GameForms,
    Ship,
    BoardForm,
)

from guess_model import (
    Guess,
    GuessEval,
)

from ranking_model import (
    RankingForm,
    RankingForms,
)

from utils import (
    getUserId,
    shipsCoordinates
)


__author__ = 'gaylord.marville@gmail.com (Gaylord Marville)'

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

TYPE_OF_BOATS = {
    "2": "Destroyer",
    "3": "Cruiser",
    "4": "Seawarship",
    "5": "Aircraft Carrier",
}

PRICE_OF_BOATS = {
    "2": 26,
    "3": 21,
    "4": 16,
    "5": 15,
}

GAME_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeGameKey=messages.StringField(1),
)

GAME_POST_REQUEST = endpoints.ResourceContainer(
    Guess,
    websafeGameKey=messages.StringField(1),
)


@endpoints.api(name='seawars',
               version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class SeaWars(remote.Service):

    """SeaWars API v1.0"""

# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

    def _copyRankingToForm(self, prof):
        """Copy relevant fields from Profile to RankingForm."""
        # copy relevant fields from Profile to RankingForm
        rf = RankingForm()
        for field in rf.all_fields():
            if hasattr(prof, field.name):
                setattr(rf, field.name, getattr(prof, field.name))
        rf.check_initialized()
        return rf

    def _copyGameToForm(self, game, displayName):
        """Copy relevant fields from Game to GameForm."""
        # copy relevant fields from Game to GameForm
        gf = GameForm()
        for field in gf.all_fields():
            if hasattr(game, field.name):
                setattr(gf, field.name, getattr(game, field.name))
            elif field.name == "websafeKey":
                setattr(gf, field.name, game.key.urlsafe())
            elif field.name == "firstPlayerId":
                setattr(gf, field.name, game.firstPlayer.playerId)
            elif field.name == "secondPlayerId":
                setattr(gf, field.name, game.secondPlayer.playerId)
        if displayName:
            setattr(gf, 'creatorDisplayName', displayName)
        gf.check_initialized()
        return gf

    def _copyGameHistoryToForm(self, game):
        """Copy relevant fields from Game to GameForm."""
        # copy relevant fields from Game to GameForm
        gh = GameForm()
        for field in gh.all_fields():
            if field.name == "websafeKey":
                setattr(gh, field.name, game.key.urlsafe())
            elif field.name == "firstPlayerR":
                setattr(gh, field.name, game.firstPlayer.rowHistory)
            elif field.name == "firstPlayerC":
                setattr(gh, field.name, game.firstPlayer.columnHistory)
            elif field.name == "secondPlayerR":
                setattr(gh, field.name, game.secondPlayer.rowHistory)
            elif field.name == "secondPlayerC":
                setattr(gh, field.name, game.secondPlayer.columnHistory)
        gh.check_initialized()
        return gh

    def _getProfileFromUser(self):
        """Return user Profile from datastore,
        creating new one if non-existent."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()
        # create new Profile if not there
        if not profile:
            profile = Profile(
                key=p_key,
                displayName=user.nickname(),
                mainEmail=user.email(),
                numberOfGame=0,
                numberOfWonGames=0,
                ranking=0,
            )
            profile.put()

        return profile      # return Profile

    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()

        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
                        prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)

    def _createGameObject(self, save_request):
        """Create Game object, returning GameForm/request."""
        # preload necessary data items
        gf = GameForm()
        # affect default dimension to boardSize if none are given
        if save_request.boardSize in (None, []):
            board_size = 10
        else:
            board_size = save_request.boardSize

        # affect default set of boat to boardSetup if none are given
        # the default set is one boat of 5 boxes, one of 4 boxes, 2 of 3 and
        # one of two
        if save_request.boardSetup in (None, []):
            board_setup = [5, 4, 3, 3, 2]
        else:
            board_setup = save_request.boardSetup

        # ship cost money, a fix amount of money is available in the wallet
        # so even if it's not implemented yet, we can imagine that for a same
        # board size two players have a different set of boat. The wallet's
        # amount is calculated according to the board size.
        wallet = board_size**2
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        prof = self._getProfileFromUser()

        for bs in board_setup:
            if str(bs) in PRICE_OF_BOATS:
                if wallet - PRICE_OF_BOATS[str(bs)] >= 0:
                    wallet -= PRICE_OF_BOATS[str(bs)]
                else:
                    raise ConflictException(
                        "Your set of ships is too expensive, you can't afford"
                        "the %s, remove a boat or choose an other one"
                        "according to the price table: %s and your"
                        "remaining credits: %s $ "
                        % (TYPE_OF_BOATS[str(bs)], PRICE_OF_BOATS, wallet))
            else:
                if wallet - (int(round((- 0.1667 * bs**3 + 3 * bs**2 -
                             17.833 * bs + 38) * bs))
                             if 2 <= bs <= 8 else 1 * bs) >= 0:
                    wallet -= (int(round((- 0.1667 * bs**3 + 3 * bs**2 -
                               17.833 * bs + 38) * bs))
                               if 2 <= bs <= 8 else 1 * bs)
                else:
                    raise ConflictException(
                        "Your set of ships is too expensive, you can't afford"
                        "the boat, remove a boat or choose an other one"
                        "according to the price table: %s and your"
                        "remaining credits: %s $ "
                        % (PRICE_OF_BOATS, wallet))

        p_key = ndb.Key(Profile, user_id)

        g_id = Game.allocate_ids(size=1, parent=p_key)[0]
        g_key = ndb.Key(Game, g_id, parent=p_key)

        setattr(gf, 'creatorUserId', user_id)
        setattr(prof, 'numberOfGame', getattr(prof, 'numberOfGame') + 1)
        prof.gameKeysToPlay.append(g_key.urlsafe())
        prof.put()

        game = Game(
            key=g_key,
            gameState="Waiting for second player",
            firstPlayer=Ship(
                playerId=user_id,
                shipsCoordinates=shipsCoordinates(board_setup, board_size),
                scoreHistory=[0],
                shipState=[0 for _ in range(len(board_setup))]),
            secondPlayer=Ship(
                shipState=[0 for _ in range(len(board_setup))]),
            numberOfPlayers=1,
            boardSize=board_size,
            boardSetup=board_setup
        )

        game.put()

        for field in gf.all_fields():
            if hasattr(game, field.name):
                setattr(gf, field.name, getattr(game, field.name))
        gf.check_initialized()

        taskqueue.add(params={'email': user.email(),
                              'conferenceInfo': repr(save_request)},
                      url='/tasks/send_confirmation_email'
                      )

        return gf

    @ndb.transactional(xg=True)
    def _gameRegistration(self, request, board_size=None, board_setup=None,
                          reg=True):
        """Register or unregister user for selected conference."""
        retval = None
        prof = self._getProfileFromUser()  # get user Profile
        user = endpoints.get_current_user()
        user_id = getUserId(user)

        # check if game exists given websafeConfKey
        # get game; check that it exists
        wsgk = request.websafeGameKey
        game = ndb.Key(urlsafe=wsgk).get()
        if not game:
            raise endpoints.NotFoundException(
                'No game found with key: %s' % wsgk)

        # register
        if reg:
            # check if user already registered otherwise add
            if wsgk in prof.gameKeysToPlay or \
               user_id == game.firstPlayer.playerId:
                raise ConflictException(
                    "You've already registered for this game")

            # check if game avail
            if game.numberOfPlayers == 2:
                raise ConflictException(
                    "The game is already full")

            # register user
            prof.gameKeysToPlay.append(wsgk)
            prof.numberOfGame += 1
            game.gameState = "In Progress"
            game.numberOfPlayers += 1
            game.secondPlayer.playerId = user_id
            game.secondPlayer.shipsCoordinates = shipsCoordinates(
                board_setup, board_size)
            game.secondPlayer.scoreHistory = [0]
            game.activePlayerId = choice([game.firstPlayer.playerId, user_id])
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsgk in prof.gameKeysToPlay:

                # unregister user, add back one seat
                if game.gameState == "Completed":
                    raise ConflictException(
                        "The game is over, it can't be escaped")
                if game.gameState == "Cancelled":
                    raise ConflictException(
                        "The game has been cancelled by his creator")

                if user_id == game.secondPlayer.playerId:
                    prof.gameKeysToPlay.remove(wsgk)
                    game.secondPlayer.playerId = None
                    game.secondPlayer.shipsCoordinates = []
                    game.secondPlayer.scoreHistory = []
                    game.numberOfPlayers -= 1
                    game.activePlayerId = None
                    game.gameState = "Waiting for second player"
                else:
                    prof.gameKeysToPlay.remove(wsgk)
                    game.numberOfPlayers -= 1
                    game.activePlayerId = None
                    game.gameState = "Cancelled"
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        game.put()
        return BooleanMessage(data=retval)

    def _switch(self, game):
        """Switch active player according to the game context"""
        if getattr(game, 'activePlayerId') == game.secondPlayer.playerId:
            return setattr(game, 'activePlayerId', game.firstPlayer.playerId)
        else:
            return setattr(game, 'activePlayerId', game.secondPlayer.playerId)

    @ndb.transactional(xg=True)
    def _guess(self, game, prof, board_setup, save_request):
        """Get the player attempt and evaluate it"""
        # preload necessary data items
        ge = GuessEval()

        ship_set_cut = [0]

        attempt = [save_request.row, save_request.column]

        # According to the active player, the coordinates of the positions
        # of the other player boats are reconstructed as well as the history
        # of the active player precedent attempts. This reconstructions
        # take the form of a two-dimensional list
        if game.activePlayerId == game.firstPlayer.playerId:
            ships = game.secondPlayer.shipsCoordinates
            rcstrd_coord = [[ships[i], ships[i + 1]]
                            for i in range(len(ships)) if i % 2 == 0]
            rcstrd_history = zip(
                game.firstPlayer.rowHistory, game.firstPlayer.columnHistory)
        else:
            ships = game.firstPlayer.shipsCoordinates
            rcstrd_coord = [[ships[i], ships[i + 1]]
                            for i in range(len(ships)) if i % 2 == 0]
            rcstrd_history = zip(
                game.secondPlayer.rowHistory, game.secondPlayer.columnHistory)

        # A list is created following this example [5, 9, 12, 15, 17]
        # for the [5, 4, 3, 3, 2] board setup
        [ship_set_cut.append(x + ship_set_cut[-1]) for x in board_setup]

        # Testing the current guess and the history
        if not tuple(attempt) in rcstrd_history:
            # Return the position of the hit ship in the list board_setup
            # else return nothing. For this board setup: [5, 4, 3, 3, 2]
            # return [0], [1], [2], [3] or [4]
            rslt = [x for x in range(len(board_setup))
                    if attempt in rcstrd_coord[
                        ship_set_cut[x]:ship_set_cut[x + 1]]]

            if getattr(game, 'activePlayerId') == \
               getattr(game.firstPlayer, 'playerId'):
                if rslt:
                    # the name of each boat from 5 to 2 boxes can be retrieve
                    # in the TYPE_OF_BOATS dictionnary, for other size the name
                    # has to be written the dict or a default name is affected
                    if str(board_setup[rslt[0]]) in TYPE_OF_BOATS:
                        class_ship = TYPE_OF_BOATS[str(board_setup[rslt[0]])]
                    else:
                        class_ship = "Unknown boat"
                    # a list initially full filled of 0 and with the same
                    # length of boardSetup help to follow the progress of the
                    # game. When a boat is hit +1 is added to his position in
                    # this list. For instance if for the first time the 4 box
                    # ship is hit for the boardSetup [5,4,3,3,2], shipState
                    # list will become [0,1,0,0,0]
                    game.firstPlayer.shipState[rslt[0]] += 1
                    if game.firstPlayer.shipState[rslt[0]] == \
                       board_setup[rslt[0]]:
                        # Saving history of the successful guess
                        game.firstPlayer.rowHistory.append(attempt[0])
                        game.firstPlayer.columnHistory.append(attempt[1])
                        game.firstPlayer.scoreHistory.append(
                            game.firstPlayer.scoreHistory[-1] + 1)
                        # if the last boat of the adversary's board is hit and
                        # sunk the if statement is proceeded
                        if game.firstPlayer.shipState == board_setup:
                            game.gameState = "Completed"
                            prof.numberOfWonGames += 1
                            setattr(
                                ge, 'guessEval', "The %s was hit and sunk, "
                                "you've won the game !" % class_ship)
                            game.firstPlayer.stateOfGuessHistory[-1] = (
                                "The %s was hit and sunk, you've "
                                "won the game !" % class_ship)
                            numberOfGuess = prof.numberOfGuess
                            numberOfShipBox = prof.numberOfShipBox
                            numberOfGuess.append(
                                len(game.firstPlayer.stateOfGuessHistory) + 1)
                            numberOfShipBox.append(sum(game.boardSetup))
                            div = sum(
                                map(truediv, numberOfGuess,
                                    numberOfShipBox)) / len(numberOfGuess)
                            prof.ranking = int(
                                (prof.numberOfWonGames * 0.9 /
                                 prof.numberOfGame) * 1000 /
                                ((div * 0.1 + 0.8) if 1 <= div <= 3 else 1.1))
                        # process if a boat is hit and sunk and its not the
                        # last of the adversary's board
                        else:
                            game.firstPlayer.stateOfGuessHistory.append(
                                "The %s was hit and sunk" % class_ship)
                            setattr(
                                ge, 'guessEval', "The %s was hit and sunk"
                                % class_ship)
                    # process if a boat is hit without being sunk
                    else:
                        game.firstPlayer.rowHistory.append(attempt[0])
                        game.firstPlayer.columnHistory.append(attempt[1])
                        game.firstPlayer.stateOfGuessHistory.append(
                            "The %s was hit" % class_ship)
                        game.firstPlayer.scoreHistory.append(
                            game.firstPlayer.scoreHistory[-1] + 1)
                        setattr(ge, 'guessEval', "The %s was hit" %
                                class_ship)
                # process if the boats are missed
                else:
                    game.firstPlayer.rowHistory.append(attempt[0])
                    game.firstPlayer.columnHistory.append(attempt[1])
                    game.firstPlayer.stateOfGuessHistory.append("Missed")
                    setattr(ge, 'guessEval', "Missed")
                    # send a mail to the other player to acknowledge him to
                    # play
                    taskqueue.add(params={'email': game.secondPlayer.playerId,
                                          'player': game.firstPlayer.playerId},
                                  url='/tasks/send_reminder_email'
                                  )
                    # switch the activePlayerId attribute for the current game
                    self._switch(game)
            else:
                if rslt:
                    if str(board_setup[rslt[0]]) in TYPE_OF_BOATS:
                        class_ship = TYPE_OF_BOATS[str(board_setup[rslt[0]])]
                    else:
                        class_ship = "Unknown boat"
                    game.secondPlayer.shipState[rslt[0]] += 1
                    if game.secondPlayer.shipState[rslt[0]] == \
                       board_setup[rslt[0]]:
                        game.secondPlayer.rowHistory.append(attempt[0])
                        game.secondPlayer.columnHistory.append(attempt[1])
                        game.secondPlayer.scoreHistory.append(
                            game.secondPlayer.scoreHistory[-1] + 1)
                        if game.secondPlayer.shipState == board_setup:
                            game.gameState = "Completed"
                            prof.numberOfWonGames += 1
                            setattr(
                                ge, 'guessEval', "The %s was hit and sunk,"
                                "you've won the game !" % class_ship)
                            game.secondPlayer.stateOfGuessHistory[-1] = (
                                "The %s was hit and sunk, "
                                "you've won the game !" % class_ship)
                            numberOfGuess = prof.numberOfGuess
                            numberOfShipBox = prof.numberOfShipBox
                            numberOfGuess.append(
                                len(game.secondPlayer.stateOfGuessHistory) + 1)
                            numberOfShipBox.append(sum(game.boardSetup))
                            div = (sum(
                                map(truediv, numberOfGuess, numberOfShipBox)) /
                                len(numberOfGuess))
                            prof.ranking = int(
                                (prof.numberOfWonGames * 0.9 /
                                 prof.numberOfGame) * 1000 /
                                ((div * 0.1 + 0.8) if 1 <= div <= 3 else 1.1))
                        else:
                            game.secondPlayer.stateOfGuessHistory.append(
                                "The %s was hit and sunk" % class_ship)
                            setattr(
                                ge, 'guessEval', "The %s was hit and sunk"
                                % class_ship)
                    else:
                        game.secondPlayer.rowHistory.append(attempt[0])
                        game.secondPlayer.columnHistory.append(attempt[1])
                        game.secondPlayer.stateOfGuessHistory.append(
                            "The %s was hit" % class_ship)
                        game.secondPlayer.scoreHistory.append(
                            game.secondPlayer.scoreHistory[-1] + 1)
                        setattr(ge, 'guessEval', "The %s was hit" %
                                class_ship)
                else:
                    game.secondPlayer.rowHistory.append(attempt[0])
                    game.secondPlayer.columnHistory.append(attempt[1])
                    game.secondPlayer.stateOfGuessHistory.append("Missed")
                    setattr(ge, 'guessEval', "Missed")
                    taskqueue.add(params={
                                  'email': game.firstPlayer.playerId,
                                  'player': game.secondPlayer.playerId},
                                  url='/tasks/send_reminder_email'
                                  )
                    self._switch(game)
        # if the player forgot he has already played this coordinates this
        # exception is raised
        else:
            raise ConflictException(
                "This coordinates were already played: %s" % rcstrd_history)

        prof.put()
        game.put()
        # return attempt
        return ge

    @endpoints.method(message_types.VoidMessage, ProfileForm,
                      path='profile', http_method='GET', name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        return self._doProfile()

    @endpoints.method(ProfileMiniForm, ProfileForm,
                      path='profile', http_method='POST',
                      name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        return self._doProfile(request)

    @endpoints.method(BoardForm, GameForm,
                      path='createGame', http_method='POST',
                      name='createTwoplayersGame')
    def createTwoplayersGame(self, request):
        """Create a two player Game"""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        return self._createGameObject(request)

    @endpoints.method(message_types.VoidMessage, GameForms,
                      path='getGamesCreated',
                      http_method='GET', name='getGamesCreated')
    def getGamesCreated(self, request):
        """Return all games created."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # create ancestor query for all key matches for this user
        games = Game.query()
        games.fetch()
        # return set of ConferenceForm objects per Conference
        return GameForms(
            items=[self._copyGameToForm(game, None) for game in games]
        )

    @endpoints.method(GAME_GET_REQUEST, GameForm,
                      path='game/{websafeGameKey}',
                      http_method='GET', name='getGame')
    def getGame(self, request):
        """Return requested game (by websafeConferenceKey)."""
        # get Game object from request; bail if not found
        game = ndb.Key(urlsafe=request.websafeGameKey).get()
        if not game:
            raise endpoints.NotFoundException(
                'No game found with key: %s' % request.websafeGameKey)
        prof = game.key.parent().get()
        if not prof:
            raise endpoints.NotFoundException(
                'No game found with key: %s' % getattr(prof, 'displayName'))
        # return GameForm
        return self._copyGameToForm(game, getattr(prof, 'displayName'))

    @endpoints.method(message_types.VoidMessage, GameForms,
                      path='getUserGames',
                      http_method='GET', name='getUserGames')
    def getUserGames(self, request):
        """Return games created by user."""
        # make sure user is authed
        games = []
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        # create ancestor query for all key matches for this user
        games = Game.query(ancestor=ndb.Key(Profile, user_id))

        # return set of GameForm objects per Game
        return GameForms(
            items=[self._copyGameToForm(game, None) for game in games]
        )

    @endpoints.method(GAME_GET_REQUEST, GameForm,
                      path='gameHistory/{websafeGameKey}',
                      http_method='GET', name='getGameHistory')
    def getGameHistory(self, request):
        """Return history of the game (by websafeConferenceKey)."""
        # get Game object from request; bail if not found
        game = ndb.Key(urlsafe=request.websafeGameKey).get()
        if not game:
            raise endpoints.NotFoundException(
                'No game found with key: %s' % request.websafeGameKey)
        # return GameForm
        return self._copyGameHistoryToForm(game)

    @endpoints.method(message_types.VoidMessage, RankingForms,
                      path='getPlayersRanking',
                      http_method='GET', name='getPlayersRanking')
    def getPlayersRanking(self, request):
        """Return the users ranking."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # create ancestor query for all key matches for this user
        profs = Profile.query()
        profs.fetch()
        return RankingForms(
            items=[self._copyRankingToForm(prof) for prof in profs]
        )

    @endpoints.method(GAME_POST_REQUEST, GuessEval,
                      path='game/{websafeGameKey}/guess',
                      http_method='POST', name='guess')
    def guess(self, request):
        """Return the guess result (by websafeConferenceKey)."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        game = ndb.Key(urlsafe=request.websafeGameKey).get()
        prof = self._getProfileFromUser()
        board_setup = getattr(game, 'boardSetup')
        board_size = getattr(game, 'boardSize')
        # the game must not have the completed status
        if getattr(game, 'gameState') == "Completed":
            raise ConflictException(
                "This game is over")
        # the game must not have the cancelled status
        if getattr(game, 'gameState') == "Cancelled":
            raise ConflictException(
                "This game has been cancelled by his creator")
        # it's impossible to play if there is only two players
        if getattr(game, 'numberOfPlayers') < 2:
            raise ConflictException(
                "Player 2 is missing, you can't play yet")
        # the player must not played if it's not his turn to play
        if getattr(game, 'activePlayerId') != getattr(prof, 'mainEmail'):
            raise ConflictException(
                "It seems it's not your turn to play")
        # You must not guess out of the board
        if not 0 <= request.row < board_size \
           and not 0 <= request.column < board_size:
            raise ConflictException(
                "You have to guess between 0 and %d" % (board_size - 1))
        if not game:
            raise endpoints.NotFoundException(
                'No game found with key: %s' % request.websafeGameKey)
        # return the guess result
        return self._guess(game, prof, board_setup, request)

    @endpoints.method(GAME_GET_REQUEST, BooleanMessage,
                      path='game/{websafeGameKey}',
                      http_method='POST', name='registerForGame')
    def registerForGame(self, request):
        """Register user for selected game."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        game = ndb.Key(urlsafe=request.websafeGameKey).get()
        board_setup = getattr(game, 'boardSetup')
        board_size = getattr(game, 'boardSize')
        return self._gameRegistration(request, board_size, board_setup)

    @endpoints.method(GAME_GET_REQUEST, BooleanMessage,
                      path='game/{websafeGameKey}',
                      http_method='DELETE', name='cancelGame')
    def cancelGame(self, request):
        """Unregister user for selected game."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        return self._gameRegistration(request, reg=False)

api = endpoints.api_server([SeaWars])  # register API
