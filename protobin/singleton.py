from protobin import Protocol


class ProtobinLoader(object):
    __instance = None
    protocols = {}

    def __new__(cls, path, server=None):
        if ProtobinLoader.__instance is None:
            ProtobinLoader.__instance = object.__new__(cls)
        return ProtobinLoader.__instance.get(path, server)

    def get(self, path, server):
        key = f'{path}|{server}'
        if key not in self.protocols:
            print('load protocol', path, server)
            self.protocols[key] = Protocol(file=path, server=server)
        return self.protocols[key]
