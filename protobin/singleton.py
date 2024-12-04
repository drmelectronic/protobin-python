from protobin import Protocol


class ProtobinLoader(object):
    __instance = None
    protocols = {}

    def __new__(cls):
        if ProtobinLoader.__instance is None:
            ProtobinLoader.__instance = object.__new__(cls)
        return ProtobinLoader.__instance

    def get(self, path):
        if path not in self.protocols:
            # print('load protocol', path)
            self.protocols[path] = Protocol(file=path)
        return self.protocols[path]
