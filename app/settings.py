import os


class Settings:
    CARD_NUMBERS_ACCEPTED = [1, 2, 3, 5, 8, 13, 21]
    MONGO_URL = os.getenv('MONGO_URL')

    def __init__(self):
        self.__validate_mongo_url()

    def __validate_mongo_url(self):
        if self.MONGO_URL is None:
            raise ValueError('MONGO_URL should be not empty')
