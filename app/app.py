from graphene import *

from fastapi import FastAPI
from mongoengine import connect, disconnect_all
from starlette.graphql import GraphQLApp

from app.resolvers.meeting_resolver import CreateMeeting, StartNewRound, Vote, MeetingQuery, FinishRound
from app.resolvers.user_resolver import CreateUser
from app.settings import Settings


settings = Settings()


class Mutation(ObjectType):
    create_user = CreateUser.Field()
    create_meeting = CreateMeeting.Field()
    start_new_round = StartNewRound().Field()
    vote = Vote().Field()
    finish_round = FinishRound.Field()


app = FastAPI()


@app.on_event('startup')
async def on_startup_fast_api():
    connect(host=settings.MONGO_URL)


@app.on_event("shutdown")
async def on_shutdown():
    disconnect_all()

app.add_route("/", GraphQLApp(schema=Schema(query=MeetingQuery, mutation=Mutation)))
