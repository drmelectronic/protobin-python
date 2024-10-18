import json
import yaml
import crcmod

from protobin.errors import InputError, FormatError
from protobin.fields import FieldBase, FIELD_MAP


class Format:

    input_fields: [FieldBase]
    output_fields: [FieldBase]

    def __init__(self, name: str, format, server: bool):
        self.name = name
        self.input_fields = []
        self.output_fields = []
        self.header = format.get('header')
        if server is None:
            input_mode = 'fields'
            output_mode = 'fields'
        else:
            input_mode = 'client' if server else 'server'
            output_mode = 'server' if server else 'client'
        for k, f in format[input_mode].items():
            if f['type'] not in FIELD_MAP:
                raise FormatError(f'Invalid protobin type {f["type"]}')
            self.input_fields.append(FIELD_MAP[f['type']](k, f))
        for k, f in format[output_mode].items():
            self.output_fields.append(FIELD_MAP[f['type']](k, f))

    def __repr__(self):
        return f'Format: {self.name} <{self.header}>'

    def encode(self, data):
        binary = b''
        if self.header:
            binary += self.header.encode('utf') + b'='
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
    crc16 = None
    crc_byteorder = None

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
        if 'crc' in js:
            self.config_crc(js['crc'])
        formats = js['formats']
        self.formats = {}
        for name in formats.keys():
            format = formats[name]
            if format.get('header') in self.headers:
                raise FormatError(f'The "{format['header']}" header is already in use at "{self.headers[format["header"]]}"')
            self.formats[name] = Format(name=name, format=format, server=self.server)
            if 'header' in format:
               self.headers[format['header']] = name

    def get_format(self, h):
        return self.formats[self.headers[h.decode('utf')]]

    def encode(self, data, format):
        if format not in self.formats:
            raise InputError(f'{format} is not available format, these are the all availables formats {self.formats.keys()}')
        return self.formats[format].encode(data)

    def decode(self, binary, codec=None):
        if codec is None:
            n = binary.find(b'=')
            h = binary[0:n]
            binary = binary[n + 1:]
            format = self.get_format(h)
            return format.name, format.decode(binary)
        format = self.formats[codec]
        data = format.decode(binary)
        return data

    def config_crc(self, js):
        self.crc16 = crcmod.mkCrcFun(int(js['poly'], 16), int(js['init'], 16), js['reverse'])
        self.crc_byteorder = js['byte_order']

    def get_crc(self, binary):
        print('crc16', self.crc16(binary).to_bytes(2, byteorder=self.crc_byteorder))
        return self.crc16(binary)
