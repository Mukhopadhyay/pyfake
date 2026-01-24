from pydantic import BaseModel


class Pyfake:

    def __init__(self):
        self.__seed = None

    @classmethod
    def generate(cls, model: BaseModel, num: int | None = 1):
        pass
