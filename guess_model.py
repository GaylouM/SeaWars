from protorpc import messages


class Guess(messages.Message):
    """Guess -- Guess outbound form message"""
    row = messages.IntegerField(1, variant=messages.Variant.INT32)
    column = messages.IntegerField(2, variant=messages.Variant.INT32)


class GuessEval(messages.Message):
    """GuessEval -- evaluation form message"""
    guessEval = messages.StringField(1)
    gameState = messages.StringField(2)
    firstPlayerHistory = messages.StringField(3)
    secondPlayerHistory = messages.StringField(4)
