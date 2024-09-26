import json

import yaml

from protobin.fields import FieldBase, FIELD_MAP


class Format:

    fields: [FieldBase]

    def __init__(self, fields: [object]):
        self.fields = []
        self.header = fields['header']
        for f in fields['format']:
            self.fields.append(FIELD_MAP[f['type']](f))

    def encode(self, data):
        binary = self.header.encode('utf') + b'='
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
        self.headers = {}
        if file:
            with open(file, 'r') as f:
                if 'json' in file:
                    js = json.loads(f.read())
                    self.load_format(js)
                elif 'yaml' in file:
                    js = yaml.full_load(f.read())
                    self.load_format(js)
        else:
            self.load_format(js)

    def load_format(self, js):
        self.formats = {}
        for k in js.keys():
            self.formats[k] = Format(js[k])
            self.headers[js[k]['header']] = k

    def get_format(self, h):
        return self.formats[self.headers[h.decode('utf')]]

    def encode(self, data, format):
        return self.formats[format].encode(data)

    def decode(self, binary):
        h, binary = binary.split(b'=')
        format = self.get_format(h)
        return h.decode('utf'), format.decode(binary)
