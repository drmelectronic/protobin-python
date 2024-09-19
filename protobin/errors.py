

class ParserError(Exception):

    def __init__(self, message):
        self._message = message
        super().__init__()

    def get_message(self):
        return self._message
