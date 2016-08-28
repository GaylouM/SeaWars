from protorpc import messages


class RegisteringForm(messages.Message):
    """BooleanMessage-- outbound Boolean value message"""
    registeringStatus = messages.StringField(1)
    activePlayerName = messages.StringField(2)
