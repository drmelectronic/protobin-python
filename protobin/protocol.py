import json
import yaml
from protobin.fields import FieldBase, FIELD_MAP


class Format:

    input_fields: [FieldBase]
    output_fields: [FieldBase]

    def __init__(self, name: str, format, server: bool):
        self.name = name
        self.input_fields = []
        self.output_fields = []
        self.header = format['header']
        if server is None:
            input_mode = 'fields'
            output_mode = 'fields'
        else:
            input_mode = 'client' if server else 'server'
            output_mode = 'server' if server else 'client'
        for k, f in format[input_mode].items():
            self.input_fields.append(FIELD_MAP[f['type']](k, f))
        for k, f in format[output_mode].items():
            self.output_fields.append(FIELD_MAP[f['type']](k, f))

    def encode(self, data):
        binary = self.header.encode('utf') + b'='
        for f in self.output_fields:
            binary += f.encode(data)
        return binary

    def decode(self, binary):
        data = {}
        for f in self.input_fields:
            val, binary = f.decode(binary)
            if f.keys:
                for k in f.keys:
                    data[k] = val[k]
            else:
                data[f.key] = val
        return data


class Protocol:

    def __init__(self, server: bool = None, file=None, js=None):
        self.server = server
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
        for name in js.keys():
            if js[name]['header'] in self.headers:
                raise KeyError(f'The "{js[name]['header']}" header is already in use at "{self.headers[js[name]["header"]]}"')
            self.formats[name] = Format(name=name, format=js[name], server=self.server)
            self.headers[js[name]['header']] = name

    def get_format(self, h):
        return self.formats[self.headers[h.decode('utf')]]

    def encode(self, data, format):
        return self.formats[format].encode(data)

    def decode(self, binary):
        n = binary.find(b'=')
        h = binary[0:n]
        binary = binary[n + 1:]
        format = self.get_format(h)
        return format.name, format.decode(binary)
