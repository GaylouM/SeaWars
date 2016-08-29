from protorpc import messages
from google.appengine.ext import ndb


class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    numberOfGames = ndb.IntegerProperty()
    numberOfWonGames = ndb.IntegerProperty()
    ranking = ndb.IntegerProperty()
    numberOfGuess = ndb.IntegerProperty(repeated=True)
    numberOfShipBox = ndb.IntegerProperty(repeated=True)
    gameKeysToPlay = ndb.StringProperty(repeated=True)


class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    displayName = messages.StringField(1)


class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName = messages.StringField(1)
    mainEmail = messages.StringField(2)
    gameKeysToPlay = messages.StringField(3, repeated=True)
    numberOfGames = messages.IntegerField(4)
    numberOfWonGames = messages.IntegerField(5)
    ranking = messages.IntegerField(6)
