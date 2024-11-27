import json
import yaml
import crcmod

from protobin.errors import InputError, FormatError, CRCError
from protobin.fields import FieldBase, FIELD_MAP


class Format:

    input_fields: [FieldBase]
    output_fields: [FieldBase]

    def __init__(self, name: str, format, server: bool):
        self.name = name
        self.input_fields = []
        self.output_fields = []
        self.header = format.get('header')
        self.crc = format.get('crc', True)
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
    crc_size = 2

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
            self.length = js['length']
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

    def encode(self, data, format_key):
        if format_key not in self.formats:
            raise InputError(f'{format_key} is not available format, these are the all availables formats {self.formats.keys()}')
        format = self.formats[format_key]
        binary = format.encode(data)
        if format.crc and self.crc16:
            binary = len(binary).to_bytes(self.length, 'big', signed=False) + binary + self.get_crc(binary)
        return binary

    def decode(self, binary, codec=None):
        if codec is None:
            n = binary.find(b'=')
            if n > 4:
                binary = self.check_crc(binary)
                n = binary.find(b'=')
            h = binary[0:n]
            binary = binary[n + 1:]
            format = self.get_format(h)
        else:
            format = self.formats[codec]
            if format.crc and self.crc16:
                binary = self.check_crc(binary)
        data = format.decode(binary)
        if codec is None:
            return format.name, data
        return data

    def check_crc(self, binary):
        length = int.from_bytes(binary[:self.length], 'big', signed=False)
        clean_binary = binary[self.length:length + self.length]
        crc = binary[length + self.length: length + self.length + self.crc_size]
        crc_value = int.from_bytes(crc, self.crc_byteorder, signed=False)
        if not crc:
            raise CRCError(f'There is no CRC')
        elif crc_value != self.crc16(clean_binary):
            raise CRCError(f'CRC no coincide {crc} != {self.get_crc(clean_binary)}')
        return clean_binary

    def config_crc(self, js):
        self.crc16 = crcmod.mkCrcFun(int(js['poly'], 16), int(js['init'], 16), js['reverse'])
        self.crc_byteorder = js['byte_order']
        if 'size' in js:
            self.crc_size = js['size']

    def get_crc(self, binary):
        return self.crc16(binary).to_bytes(self.crc_size, byteorder=self.crc_byteorder)
