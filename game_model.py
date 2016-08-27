from protorpc import messages
from google.appengine.ext import ndb


class Ship(ndb.Model):
    """Ship -- Ship object"""
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
    firstPlayer = ndb.StructuredProperty(Ship)
    secondPlayer = ndb.StructuredProperty(Ship)
    numberOfPlayers = ndb.IntegerProperty()
    boardSize = ndb.IntegerProperty()
    boardSetup = ndb.IntegerProperty(repeated=True)


class GameForm(messages.Message):
    """GameForm -- Game outbound form message"""
    creatorUserId = messages.StringField(1)
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


class BoardForm(messages.Message):
    """BoardForm -- Board form message"""
    boardSize = messages.IntegerField(1)
    boardSetup = messages.IntegerField(2, repeated=True)
