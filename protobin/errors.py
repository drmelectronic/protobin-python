

class BaseError(Exception):

    def __init__(self, message):
        self._message = message
        super().__init__()

    def __str__(self):
        return self._message

    def get_message(self):
        return self._message


class FormatError(BaseError):
    pass


class InputError(BaseError):
    pass


class DecodeError(BaseError):
    pass


class CRCError(BaseError):
    pass
