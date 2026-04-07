class PyfakeError(Exception):
    pass


class GeneratorNotFound(PyfakeError):
    def __init__(self, type_):
        super().__init__(f"No generator registered for type {type_}")


class InvalidConstraints(PyfakeError):
    def __init__(self, message):
        super().__init__(message)
