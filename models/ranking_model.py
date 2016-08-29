from protorpc import messages


class RankingForm(messages.Message):
    """RankingForm -- Ranking form message"""
    displayName = messages.StringField(1)
    ranking = messages.IntegerField(2)


class RankingForms(messages.Message):
    """RankingForms -- multiple Ranking outbound form message"""
    items = messages.MessageField(RankingForm, 1, repeated=True)
