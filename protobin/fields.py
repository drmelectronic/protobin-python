import enum
import datetime
import math
from typing import Union, List

from protobin.errors import ParserError


class FieldEnum(enum.StrEnum):
    ARRAY = 'array'
    BITS = 'bits'
    BOOL = 'bool'
    CHAR = 'char'
    DATE = 'date'
    DATETIME = 'datetime'
    ID = 'id'
    FLAGS = 'flags'
    FLOAT = 'float'
    SIGNED = 'signed'
    STRING = 'string'
    TIME = 'time'
    TIMESTAMP = 'timestamp'
    UNSIGNED = 'unsigned'


class FieldBase:
    bytes: int | None
    key: Union[str, List[str]]
    type: FieldEnum

    def __init__(self, k, js):
        self.key = k
        self.type = js['type']
        self.bytes = js.get('bytes')

    def decode(self, binary):
        self.ensure_length(binary)
        a, b = self.split(binary)
        val = self.from_binary(a)
        return val, b

    def encode(self, data):
        val = data.get(self.key)
        return self.to_binary(val)

    def ensure_length(self, binary):
        if self.bytes:
            if len(binary) < self.bytes:
                raise ParserError('Binary has not enough data')

    def from_binary(self, binary):
        raise NotImplementedError()

    @staticmethod
    def to_int(n):
        lo = n % 16
        hi = n // 16
        return hi * 10 + lo

    @staticmethod
    def get_nible(binary):
        hexa = ord(binary[0:1])
        lo = hexa % 16
        hi = hexa // 16
        nible = hi * 10 + lo
        return nible, binary[1:]

    def to_binary(self, val):
        raise NotImplementedError()

    def to_nible(self, n):
        tens = int(n / 10)
        units = n % 10
        return int(tens * 16 + units)

    def split(self, binary):
        if self.bytes:
            return binary[:self.bytes], binary[self.bytes:]
        return binary[1:binary[0] + 1], binary[binary[0] + 1:]



class FieldArray(FieldBase):
    length: int

    def __init__(self, k, js):
        super().__init__(k, js)
        self.array = js['array']

    def decode(self, binary):
        self.length = binary[0]
        binary = binary[1:]
        val, binary = self.from_binary(binary)
        return val, binary

    def to_binary(self, val):
        binary = b''
        length = len(val)
        binary += length.to_bytes(1, 'big')
        for i in range(length):
            fields = [FIELD_MAP[f['type']](k, f) for k, f in self.array.items()]
            for f in fields:
                binary += f.encode(val[i])
        return binary

    def from_binary(self, binary):
        lista = []
        for i in range(self.length):
            data = {}
            fields = [FIELD_MAP[f['type']](k, f) for k, f in self.array.items()]
            for f in fields:
                val, binary = f.decode(binary)
                data[f.key] = val
            lista.append(data)
        return lista, binary


class FieldBits(FieldBase):
    length: int

    def __init__(self, k, js):
        super().__init__(k, js)
        self.length = js.get('length', 0)
        self.bytes = math.ceil(self.length / 8)

    def decode(self, binary):
        self.ensure_length(binary)
        a, b, length = self.split(binary)
        val = self.from_binary_bits(a, length)
        return val, b

    def split(self, binary):
        if self.length:
            return binary[:self.bytes], binary[self.bytes:], self.length
        length = binary[0]
        bts = math.ceil(length / 8)
        return binary[1:bts + 1], binary[bts + 1:], length

    def to_binary(self, val: List[bool]):
        if len(val) == 0:
            return b'\x00'
        binary = b''
        if len(val) % 8:
            bits = '0' * (8 - (len(val) % 8))
        else:
            bits = ''
        for b in val:
            bits += '1' if b else '0'
        bts = int(len(bits) / 8)
        if not self.length:
            binary += len(val).to_bytes(1, 'big', signed=False)
        binary += int(bits, 2).to_bytes(bts, 'big', signed=False)
        return binary

    def from_binary_bits(self, binary, length):
        numero = int.from_bytes(binary, 'big', signed=False)
        bits = bin(numero)[2:]
        val = [False] * 8
        for b in bits:
            val.append(b == '1')
        val = val[-length:]
        return val


class FieldBool(FieldBase):

    bytes = 1

    def to_binary(self, val):
        if val is None:
            val = 2
        else:
            val = bool(val)

        return val.to_bytes(1, 'big', signed=False)

    def from_binary(self, binary):
        val = int.from_bytes(binary, 'big', signed=False)
        if val == 0:
            return False
        elif val == 1:
            return True
        else:
            return None


class FieldChar(FieldBase):
    bytes = 1

    def to_binary(self, val):
        if val is None:
            return b''
        return val.encode('utf')

    def from_binary(self, binary):
        return binary[:self.bytes].decode('utf')


class FieldDate(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = 3

    def to_binary(self, val: datetime.datetime | str):
        if isinstance(val, str):
            val = datetime.datetime.strptime(val, '%Y-%m-%d').date()
        return bytes([
            self.to_nible(val.day),
            self.to_nible(val.month),
            self.to_nible(val.year - 2000)
        ])

    def from_binary(self, binary):
        d, binary = self.get_nible(binary)
        m, binary = self.get_nible(binary)
        y, binary = self.get_nible(binary)
        return datetime.datetime(2000 + y, m, d).date()


class FieldDateTime(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = 6

    def to_binary(self, val: datetime.datetime | str):
        if val is None:
            val = datetime.datetime(2000, 1, 1)
        elif not isinstance(val, datetime.datetime):
                raise ValueError(f'Error en el campo "{self.key}" se espera un datetime pero se recibe {val}')
        elif isinstance(val, str):
            val = datetime.datetime.strptime(val, '%Y-%m-%d %H:%M:%S').date()
        return bytes([
            self.to_nible(val.day),
            self.to_nible(val.month),
            self.to_nible(val.year - 2000),
            self.to_nible(val.hour),
            self.to_nible(val.minute),
            self.to_nible(val.second)
        ])

    def from_binary(self, binary):
        d, binary = self.get_nible(binary)
        m, binary = self.get_nible(binary)
        y, binary = self.get_nible(binary)
        H, binary = self.get_nible(binary)
        M, binary = self.get_nible(binary)
        S, binary = self.get_nible(binary)
        return datetime.datetime(2000 + y, m, d, H, M, S)


class FieldFlags(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.key = self.key.split(',')
        self.length = len(self.key)
        self.bytes = math.ceil(self.length / 8)

    def encode(self, data):
        return self.to_binary(data)

    def from_binary(self, binary):
        numero = int.from_bytes(binary[:self.bytes], 'big', signed=False)
        bits = bin(numero)[2:]
        flags = [False] * 8
        for b in bits:
            flags.append(b == '1')
        val = {}
        order = -len(self.key)
        for k in self.key:
            val[k] = flags[order]
            order += 1
        return val

    def to_binary(self, data):
        bits = '0' * (8 - (len(self.key) % 8))
        for k in self.key:
            bits += '1' if data[k] else '0'
        return int(bits, 2).to_bytes(self.bytes, 'big', signed=False)


class FieldFloat(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.decimals = js['decimals']

    def from_binary(self, binary):
        val = int.from_bytes(binary[:self.bytes], 'big', signed=True)
        return val / (10 ** self.decimals)

    def to_binary(self, val):
        return int(round(val * (10 ** self.decimals))).to_bytes(self.bytes, 'big', signed=True)


class FieldId(FieldBase):

    def to_binary(self, val):
        if val is None:
            val = 0
        max_value = 256 ** self.bytes - 1
        val = min(val, max_value)
        if val < 0:
            raise ValueError('Negative values not allowed')
        return int(val).to_bytes(self.bytes, 'big', signed=False)

    def from_binary(self, binary):
        val = int.from_bytes(binary[:self.bytes], 'big', signed=False)
        if val == 0:
            val = None
        return val


class FieldSigned(FieldBase):

    def to_binary(self, val):
        if val is None:
            val = 0
        maximo = 256 ** self.bytes / 2 - 1
        minimo = - maximo - 1
        val = max(min(val, maximo), minimo)
        return int(val).to_bytes(self.bytes, 'big', signed=True)

    def from_binary(self, binary):
        return int.from_bytes(binary, 'big', signed=True)


class FieldString(FieldBase):

    def to_binary(self, val):
        if self.bytes:
            utf = str(val).encode('utf')[:self.bytes]
            return utf
        utf = str(val).encode('utf')[:255]
        return len(utf).to_bytes(1, 'big') + utf

    def from_binary(self, binary):
        return binary.decode('utf')


class FieldTime(FieldBase):

    bytes = 2

    def to_binary(self, val: datetime.datetime | datetime.time | str):
        if val is None:
            val = datetime.time(0, 0)
        elif not isinstance(val, datetime.datetime) and not isinstance(val, datetime.time):
                raise ValueError(f'Error en el campo "{self.key}" se espera un datetime o time pero se recibe {val}')
        elif isinstance(val, str):
            val = datetime.datetime.strptime(val, '%H:%M').date()
        return bytes([
            self.to_nible(val.hour),
            self.to_nible(val.minute)
        ])

    def from_binary(self, binary):
        H, binary = self.get_nible(binary)
        M, binary = self.get_nible(binary)
        if H == 0 and M == 0:
            return None
        return datetime.time(H, M)


class FieldTimestamp(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = 8

    def to_binary(self, val: datetime.datetime | str):
        timestamp = val.timestamp() * 1000000
        return int(timestamp).to_bytes(8, 'big', signed=False)

    def from_binary(self, binary):
        d = int.from_bytes(binary, 'big')
        return datetime.datetime.fromtimestamp(d / 1000000)


class FieldUnsigned(FieldBase):

    def to_binary(self, val):
        if val is None:
            raise ValueError(f'Error en el campo "{self.key}" no se permite None')
        max_value = 256 ** self.bytes - 1
        val = min(val, max_value)
        if val < 0:
            raise ValueError(f'Error en el campo "{self.key}" se espera enteros positivos y se recibió {val}')
        return int(val).to_bytes(self.bytes, 'big', signed=False)

    def from_binary(self, binary):
        return int.from_bytes(binary[:self.bytes], 'big', signed=False)


FIELD_MAP = {
    'array': FieldArray,
    'bits': FieldBits,
    'bool': FieldBool,
    'char': FieldChar,
    'date': FieldDate,
    'datetime': FieldDateTime,
    'flags': FieldFlags,
    'float': FieldFloat,
    'id': FieldId,
    'signed': FieldSigned,
    'string': FieldString,
    'time': FieldTime,
    'timestamp': FieldTimestamp,
    'unsigned': FieldUnsigned,
}
