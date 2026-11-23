class PyfakeError(Exception):
    pass


class GeneratorNotFound(PyfakeError):
    def __init__(self, type_: type, path: str | None = None) -> None:
        self.type = type_
        self.path = path
        location = f" (field '{path}')" if path else ""
        super().__init__(
            f"No generator registered for type {type_}{location}. "
            "Use a supported type or give the field a default value."
        )


class InvalidConstraints(PyfakeError, ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidOverride(PyfakeError, ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
