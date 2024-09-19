import json

from protobin.fields import FieldBase, FIELD_MAP


class Format:

    fields: [FieldBase]

    def __init__(self, fields: [object]):
        self.fields = []
        for f in fields:
            self.fields.append(FIELD_MAP[f['type']](f))

    def encode(self, data):
        binary = b''
        for f in self.fields:
            binary += f.encode(data)
        return binary

    def decode(self, binary):
        data = {}
        for f in self.fields:
            val, binary = f.decode(binary)
            if f.key:
                data[f.key] = val
            else:
                for k in f.keys:
                    data[k] = val[k]
        return data

    def to_dict(self):
        return [f.to_dict() for f in self.fields]


class Protocol:

    def __init__(self, file=None, js=None):
        if file:
            with open(file, 'r') as f:
                js = json.loads(f.read())
        self.formats = {}
        for k in js.keys():
            self.formats[k] = Format(js[k])

    def temp_format(self, k):
        return self.formats[k].to_dict()

    def encode(self, data, format):
        return self.formats[format].encode(data)

    def decode(self, binary, format):
        return self.formats[format].decode(binary)
