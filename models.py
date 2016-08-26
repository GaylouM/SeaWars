#!/usr/bin/env python

"""models.py

Seawars server-side Python App Engine data & ProtoRPC models

$Id: models.py,v 1.0 2016/08/26 22:01:10 GaylouM $

"""
import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb


class ConflictException(endpoints.ServiceException):
    """ConflictException -- exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT


class Attempt(messages.Message):
    """Attempt -- attempt form message"""
    attempt = messages.IntegerField(1)


class AttemptEval(messages.Message):
    """AttemptEval -- evaluation form message"""
    attemptEval = messages.StringField(1)


class Board(ndb.Model):
    """Board -- Board object"""
    boardSize = ndb.IntegerProperty()
    boardSetup = ndb.IntegerProperty(repeated=True)


class BoardForm(messages.Message):
    """BoardForm -- Board form message"""
    boardSize = messages.IntegerField(1)
    boardSetup = messages.IntegerField(2, repeated=True)


class BooleanMessage(messages.Message):
    """BooleanMessage-- outbound Boolean value message"""
    data = messages.BooleanField(1)


class ShipNPlayer(ndb.Model):
    """ShipNPlayer -- ShipNPlayer object"""
    playerId = ndb.StringProperty()
    shipsCoordinates = ndb.IntegerProperty(repeated=True)
    rowHistory = ndb.IntegerProperty(repeated=True)
    columnHistory = ndb.IntegerProperty(repeated=True)
    stateOfGuessHistory = ndb.StringProperty(repeated=True)
    scoreHistory = ndb.IntegerProperty(repeated=True)
    shipState = ndb.IntegerProperty(repeated=True)


class Game(ndb.Model):
    """Game -- Game object"""
    gameState = ndb.StringProperty()
    activePlayerId = ndb.StringProperty()
    firstPlayer = ndb.StructuredProperty(ShipNPlayer)
    secondPlayer = ndb.StructuredProperty(ShipNPlayer)
    numberOfPlayers = ndb.IntegerProperty()
    boardSize = ndb.IntegerProperty()
    boardSetup = ndb.IntegerProperty(repeated=True)


class GameForm(messages.Message):
    """GameForm -- Game outbound form message"""
    organizerUserId = messages.StringField(1)
    websafeKey = messages.StringField(2)
    creatorDisplayName = messages.StringField(3)
    numberOfPlayers = messages.IntegerField(4)
    gameState = messages.StringField(5)
    activePlayerId = messages.StringField(6)
    boardSize = messages.IntegerField(7)
    boardSetup = messages.IntegerField(8, repeated=True)
    firstPlayerR = messages.IntegerField(9, repeated=True)
    firstPlayerC = messages.IntegerField(10, repeated=True)
    secondPlayerR = messages.IntegerField(11, repeated=True)
    secondPlayerC = messages.IntegerField(12, repeated=True)


class GameForms(messages.Message):
    """GameForms -- multiple Game outbound form message"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class Guess(messages.Message):
    """Guess -- Guess outbound form message"""
    row = messages.IntegerField(1, variant=messages.Variant.INT32)
    column = messages.IntegerField(2, variant=messages.Variant.INT32)


class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    numberOfGame = ndb.IntegerProperty()
    numberOfWonGames = ndb.IntegerProperty()
    ranking = ndb.IntegerProperty()
    numberOfGuess = ndb.IntegerProperty(repeated=True)
    numberOfShipBox = ndb.IntegerProperty(repeated=True)
    gameKeysToPlay = ndb.StringProperty(repeated=True)


class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    displayName = messages.StringField(1)
    numberOfGame = messages.IntegerField(2)
    numberOfWonGames = messages.IntegerField(3)


class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName = messages.StringField(1)
    mainEmail = messages.StringField(2)
    gameKeysToPlay = messages.StringField(3, repeated=True)
    numberOfGame = messages.IntegerField(4)
    numberOfWonGames = messages.IntegerField(5)
    ranking = messages.IntegerField(6)


class RankingForm(messages.Message):
    """RankingForm -- Ranking form message"""
    displayName = messages.StringField(1)
    ranking = messages.IntegerField(2)


class RankingForms(messages.Message):
    """RankingForms -- multiple Ranking outbound form message"""
    items = messages.MessageField(RankingForm, 1, repeated=True)


class ShipCoordinates(ndb.Model):
    """ShipCoordinates -- ShipCoordinates object"""
    row = ndb.IntegerProperty(required=True)
    columns = ndb.IntegerProperty(required=True)


class History(ndb.Model):
    """History -- History object"""
    row = ndb.IntegerProperty()
    column = ndb.IntegerProperty()
    stateOfGuess = ndb.StringProperty()
    score = ndb.IntegerProperty()
