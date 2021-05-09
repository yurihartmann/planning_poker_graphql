from graphene import *
from graphql import GraphQLError

from app.models.meeting import Meeting
from app.models.user import User
from app.resolvers.user_resolver import UserSchema
from app.settings import Settings


class RoundSchema(ObjectType):
    round_counter = Int()
    votes = List(Int)
    finished = Boolean()
    winner_round = Int()


class MeetingSchema(ObjectType):
    id = String()
    name = String()
    admin = Field(UserSchema)
    rounds = List(RoundSchema)


class MeetingQuery(ObjectType):
    get_meeting = Field(MeetingSchema, meeting_id=String(required=True))

    def resolve_get_meeting(root, info, meeting_id):
        meeting = Meeting.objects(id=meeting_id).first()
        if not meeting:
            raise GraphQLError('Meeting with this id do not exists')

        return MeetingSchema(
                id=str(meeting.id),
                name=meeting.name,
                admin=UserSchema(email=meeting.admin.email, name=meeting.admin.name),
                rounds=[RoundSchema(
                    round_counter=round.round_counter,
                    votes=[vote.card_number for vote in round.votes],
                    winner_round=round.get_card_number_winner(),
                    finished=round.finished
                ) for round in meeting.rounds if round.finished]
            )


class CreateMeeting(Mutation):
    class Arguments:
        admin_email = String(required=True)
        name = String(required=True)

    meeting = Field(MeetingSchema)

    def mutate(self, info, admin_email, name):
        user = User.objects(email=admin_email).first()
        if not user:
            raise GraphQLError('User with this email do not exists')

        meeting = Meeting(name=name, admin=user).save()

        return CreateMeeting(meeting=MeetingSchema(
                id=str(meeting.id),
                name=meeting.name,
                admin=UserSchema(email=user.email, name=user.name)
            )
        )


class StartNewRound(Mutation):
    class Arguments:
        admin_email = String(required=True)
        meeting_id = String(required=True)

    meeting = Field(MeetingSchema)

    def mutate(self, info, meeting_id, admin_email):
        user = User.objects(email=admin_email).first()
        if not user:
            raise GraphQLError('User with this email do not exists')

        meeting = Meeting.objects(id=meeting_id).first()
        if not meeting:
            raise GraphQLError('Meeting with this id do not exists')

        meeting.create_new_round()

        return StartNewRound(meeting=MeetingSchema(
                id=str(meeting.id),
                name=meeting.name,
                admin=UserSchema(email=user.email, name=user.name),
                rounds=[RoundSchema(
                    round_counter=meeting.rounds[-1].round_counter
                )]
            )
        )


class FinishRound(Mutation):
    class Arguments:
        admin_email = String(required=True)
        meeting_id = String(required=True)

    meeting = Field(MeetingSchema)

    def mutate(self, info, meeting_id, admin_email):
        user = User.objects(email=admin_email).first()
        if not user:
            raise GraphQLError('User with this email do not exists')

        meeting = Meeting.objects(id=meeting_id).first()
        if not meeting:
            raise GraphQLError('Meeting with this id do not exists')

        if meeting.admin != user:
            raise GraphQLError('You do not have permission for fished rounds in this meeting')

        meeting.finished_round()

        return StartNewRound(meeting=MeetingSchema(
                id=str(meeting.id),
                name=meeting.name,
                admin=UserSchema(email=user.email, name=user.name),
                rounds=[RoundSchema(
                    round_counter=round.round_counter,
                    votes=[vote.card_number for vote in round.votes],
                    winner_round=round.get_card_number_winner(),
                    finished=round.finished
                ) for round in meeting.rounds if round.finished]
            )
        )


class Vote(Mutation):
    class Arguments:
        email = String(required=True)
        meeting_id = String(required=True)
        card_number = Int(required=True)

    meeting = Field(MeetingSchema)

    def mutate(self, info, email, meeting_id, card_number):
        user = User.objects(email=email).first()
        if not user:
            raise GraphQLError('User with this email do not exists')

        meeting = Meeting.objects(id=meeting_id).first()
        if not meeting:
            raise GraphQLError('Meeting with this id do not exists')

        if meeting.rounds[-1].finished:
            raise GraphQLError('Round finished, wait next round')

        if card_number not in Settings.CARD_NUMBERS_ACCEPTED:
            raise GraphQLError(f'Card number only accept {Settings.CARD_NUMBERS_ACCEPTED}')

        meeting.vote(user, card_number)

        return Vote(meeting=MeetingSchema(
                id=str(meeting.id),
                name=meeting.name,
                admin=UserSchema(email=user.email, name=user.name),
                rounds=[RoundSchema(
                    round_counter=meeting.rounds[-1].round_counter,
                    votes=[vote.card_number for vote in meeting.rounds[-1].votes if vote.user == user]
                )]
            )
        )
