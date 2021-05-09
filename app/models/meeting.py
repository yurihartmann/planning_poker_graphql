from mongoengine import *

from app.models.user import User


class Vote(EmbeddedDocument):
    user = ReferenceField(User, required=True)
    card_number = IntField(min_value=0, max_value=21)


class Round(EmbeddedDocument):
    round_counter = IntField(primary_key=True)
    votes = EmbeddedDocumentListField(Vote, default=[])
    finished = BooleanField(default=False)

    def get_card_number_winner(self) -> int:
        results = {}
        for vote in self.votes:
            if results.get(str(vote.card_number)):
                results[str(vote.card_number)] += 1
            else:
                results[str(vote.card_number)] = 1

        return int(max(results, key=results.get))


class Meeting(Document):
    name = StringField(required=True)
    admin = ReferenceField(User, required=True)
    rounds = EmbeddedDocumentListField(Round, default=[])

    meta = {
        'collection': 'meetings'
    }

    def create_new_round(self):
        if not self.rounds:
            new_round = Round(round_counter=1)
            self.rounds = [new_round]
        else:
            self.rounds[-1].finished = True
            n = self.rounds[-1].round_counter + 1
            new_round = Round(round_counter=n)
            self.rounds.append(new_round)

        self.save()

    def vote(self, user, card_number):
        if not self.rounds[-1].votes:
            vote = Vote(user=user, card_number=card_number)
            self.rounds[-1].votes = [vote]
        else:
            voted = False
            for vote in self.rounds[-1].votes:
                if vote.user == user:
                    vote.card_number = card_number
                    voted = True
                    break

            if not voted:
                self.rounds[-1].votes.append(Vote(user=user, card_number=card_number))

        self.save()

    def finished_round(self):
        self.rounds[-1].finished = True
        self.save()
