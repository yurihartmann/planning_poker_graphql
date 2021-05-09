from graphene import *

from app.models.user import User


class UserSchema(ObjectType):
    email = String()
    name = String()


class CreateUser(Mutation):
    class Arguments:
        email = String(required=True)
        name = String(required=True)

    user = Field(UserSchema)

    def mutate(self, info, name, email):
        user = User(email=email, name=name)
        user.save()

        return CreateUser(
            user=UserSchema(
                email=user.email,
                name=user.name,
            )
        )
