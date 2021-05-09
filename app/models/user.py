from mongoengine import *


class User(Document):
    email = StringField(unique=True, required=True)
    name = StringField(required=True)

    meta = {
        'collection': 'users'
    }
