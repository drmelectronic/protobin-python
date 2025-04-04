import enum
import datetime
import math
from typing import Union, List

from protobin.errors import DecodeError, FormatError


# removed for python 3.8
# class FieldEnum(enum.StrEnum):
#     ARRAY = 'array'
#     BITS = 'bits'
#     BOOL = 'bool'
#     CHAR = 'char'
#     DATE = 'date'
#     DATETIME = 'datetime'
#     ID = 'id'
#     FLAGS = 'flags'
#     FLOAT = 'float'
#     SIGNED = 'signed'
#     STRING = 'string'
#     TIME = 'time'
#     TIMESTAMP = 'timestamp'
#     UNSIGNED = 'unsigned'


class FieldBase:
    # removed for python 3.8
    # bytes: int | None
    # keys: List[str] | None
    # key: str
    # type: FieldEnum

    def __init__(self, k, js):
        self.key = k
        self.keys = None
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
                raise DecodeError(f'Binary has not enough data for {self}')

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


class ArrayField(FieldBase):
    length: int

    def __init__(self, k, js):
        super().__init__(k, js)
        fields = []
        for k, f in js['array'].items():
            if f['type'] not in FIELD_MAP:
                raise FormatError(f'Invalid protobin type {f["type"]}')
            fields.append(FIELD_MAP[f['type']](k, f))
        self.fields = fields

    def __repr__(self):
        return f'ArrayField<key: {self.key}>'

    def decode(self, binary):
        length = binary[0]
        binary = binary[1:]
        val, binary = self.from_binary(binary, length)
        return val, binary

    def to_binary(self, val):
        if not isinstance(val, (list, tuple)):
            raise ValueError(f'Error in field ArrayField<{self.key}>, a array is expected but "{val}" is received, {type(val)}')
        binary = b''
        length = len(val)
        binary += length.to_bytes(1, 'big')
        for i in range(length):
            for f in self.fields:
                binary += f.encode(val[i])
        return binary

    def from_binary(self, binary, length):
        lista = []
        for i in range(length):
            data = {}
            for f in self.fields:
                val, binary = f.decode(binary)
                data[f.key] = val
            lista.append(data)
        return lista, binary


class BitsField(FieldBase):
    length: int

    def __init__(self, k, js):
        super().__init__(k, js)
        self.length = js.get('length', 0)
        self.bytes = math.ceil(self.length / 8)

    def __repr__(self):
        return f'BitsField<key: {self.key}, length: {self.length}, bytes: {self.bytes}>'

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


class BoolField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = 1

    def __repr__(self):
        return f'BoolField<key: {self.key}>'

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


class CharField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = js.get('bytes', 1)

    def __repr__(self):
        return f'CharField<key: {self.key}>'

    def to_binary(self, val):
        if val is None:
            return bytes([0])
        encoded = val[:self.bytes].encode('utf')
        if self.bytes == 1 and len(encoded) > 1:
            raise ValueError(f'{self} of one byte is possible to encode a utf-8 character')
        i = 0
        while len(encoded) > self.bytes:
            i += 1
            encoded = val[:self.bytes - i].encode('utf')
        return (encoded + b' ' * self.bytes)[:self.bytes]

    def from_binary(self, binary):
        val = int.from_bytes(binary[:self.bytes], 'big', signed=False)
        if val == 0:
            return None
        return binary[:self.bytes].decode('utf')


class DateField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = 3

    def __repr__(self):
        return f'DateField<key: {self.key}>'

    # removed for python 3.8
    # def to_binary(self, val: datetime.datetime | str):
    def to_binary(self, val):
        if val is None:
            return bytes([0] * 3)
        elif isinstance(val, str):
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
        if y == 0 and m == 0 and d == 0:
            return None
        return datetime.datetime(2000 + y, m, d).date()


class DateTimeField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = 6

    def __repr__(self):
        return f'DateTimeField<key: {self.key}>'

    # removed for python 3.8
    # def to_binary(self, val: datetime.datetime | str):
    def to_binary(self, val):
        if val is None:
            return bytes([0] * 6)
        elif not isinstance(val, datetime.datetime):
            raise ValueError(f'Error in field DateTimeField<{self.key}>, a datetime is expected but "{val}" is received')
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
        if y == 0 and m == 0 and d == 0 and H == 0 and M == 0 and S == 0:
            return None
        return datetime.datetime(2000 + y, m, d, H, M, S)


class FlagsField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.keys = self.key.split(',')
        self.length = len(self.keys)
        self.bytes = math.ceil(self.length / 8)

    def __repr__(self):
        return f'FlagsField<keys: {self.keys}, length: {self.length}, bytes: {self.bytes}>'

    def encode(self, data):
        return self.to_binary(data)

    def from_binary(self, binary):
        numero = int.from_bytes(binary[:self.bytes], 'big', signed=False)
        bits = bin(numero)[2:]
        flags = [False] * 8
        for b in bits:
            flags.append(b == '1')
        val = {}
        order = -len(self.keys)
        for k in self.keys:
            val[k] = flags[order]
            order += 1
        return val

    def to_binary(self, data, allow_none=False):
        bits = '0' * (8 - (len(self.keys) % 8))
        for k in self.keys:
            val = data.get(k)
            if val is None:
                raise ValueError(f'Error in field FlagsField<{self.key}>, a boolean is expected but "None" is received')
            bits += '1' if data[k] else '0'
        return int(bits, 2).to_bytes(self.bytes, 'big', signed=False)


class FloatField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.decimals = js.get('decimals', None)
        if self.bytes == None:
            raise ValueError(f'FloatField<{self.key}> needs to have bytes declared')
        if self.decimals == None:
            raise ValueError(f'FloatField<{self.key}> needs to have decimals declared')

    def __repr__(self):
        return f'FloatField<key: {self.key}, bytes: {self.bytes}, decimals: {self.decimals}>'

    def from_binary(self, binary):
        val = int.from_bytes(binary[:self.bytes], 'big', signed=True)
        return val / (10 ** self.decimals)

    def to_binary(self, val):
        return int(round(val * (10 ** self.decimals))).to_bytes(self.bytes, 'big', signed=True)


class IdField(FieldBase):

    def __repr__(self):
        return f'IdField<key: {self.key}, bytes: {self.bytes}>'

    def to_binary(self, val):
        if val is None:
            val = 0
        max_value = 256 ** self.bytes - 1
        val = min(val, max_value)
        if val < 0:
            raise ValueError('IdField<{self.key}> does not allow negative values')
        return int(val).to_bytes(self.bytes, 'big', signed=False)

    def from_binary(self, binary):
        val = int.from_bytes(binary[:self.bytes], 'big', signed=False)
        if val == 0:
            val = None
        return val


class SignedField(FieldBase):

    def __repr__(self):
        return f'SignedField<key: {self.key}, bytes: {self.bytes}>'

    def to_binary(self, val):
        if val is None:
            val = 0
        maximo = 256 ** self.bytes / 2 - 1
        minimo = - maximo - 1
        val = max(min(val, maximo), minimo)
        return int(val).to_bytes(self.bytes, 'big', signed=True)

    def from_binary(self, binary):
        return int.from_bytes(binary, 'big', signed=True)


class StringField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.length_size = js.get('length_size', 1)

    def __repr__(self):
        return f'StringField<key: {self.key}, bytes: {self.bytes}>'

    def from_binary(self, binary):
        try:
            return binary.decode('utf')
        except UnicodeEncodeError:
            raise DecodeError(f"{self}: Can't decode string: {binary}")

    def split(self, binary):
        if self.bytes:
            return binary[:self.bytes], binary[self.bytes:]
        bytes = int.from_bytes(binary[:self.length_size], 'big', signed=False)
        return binary[self.length_size:bytes + self.length_size], binary[bytes + self.length_size:]

    def to_binary(self, val):
        if self.bytes:
            utf = str(val).encode('utf')[:self.bytes]
            return utf
        if val is None:
            utf = b''
        else:
            utf = str(val).encode('utf')[:255]
        return len(utf).to_bytes(self.length_size, 'big') + utf


class TimeField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = 2

    def __repr__(self):
        return f'TimeField<key: {self.key}, bytes: {self.bytes}>'

    # removed for python 3.8
    # def to_binary(self, val: datetime.datetime | datetime.time | str):
    def to_binary(self, val):
        if val is None:
            return bytes([0] * 2)
        elif isinstance(val, str):
            try:
                if len(val) > 5:
                    val = datetime.datetime.strptime(val, '%Y-%m-%d %H:%M:%S').time()
                else:
                    val = datetime.datetime.strptime(val, '%H:%M').time()
            except:
                raise ValueError(f'Error in field TimeField<{self.key}>, a datetime or time is expected but "{val}" is received')

        elif not isinstance(val, datetime.datetime) and not isinstance(val, datetime.time):
            raise ValueError(f'Error in field TimeField<{self.key}>, a datetime or time is expected but "{val}" is received')

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


class TimestampField(FieldBase):

    def __init__(self, k, js):
        super().__init__(k, js)
        self.bytes = js.get('bytes', 6)
        self.decimals = js.get('decimals', 6)

    def __repr__(self):
        return f'TimestampField<key: {self.key}>'

    # removed for python 3.8
    # def to_binary(self, val: datetime.datetime | str):
    def to_binary(self, val):
        if val is None:
            return bytes([0] * 8)
        timestamp = val.timestamp() * (10 ** self.decimals)
        return int(timestamp).to_bytes(self.bytes, 'big', signed=False)

    def from_binary(self, binary):
        d = int.from_bytes(binary, 'big')
        if d == 0:
            return None
        return datetime.datetime.fromtimestamp(d / (10 ** self.decimals))


class UnsignedField(FieldBase):

    def __repr__(self):
        return f'UnsignedField<key: {self.key}, bytes: {self.bytes}>'

    def encode(self, data):
        val = data.get(self.key, 0)
        return self.to_binary(val)

    def to_binary(self, val):
        if val is None:
            raise ValueError(f'Error in field UnsignedField<{self.key}>, None is not allowed')
        max_value = 256 ** self.bytes - 1
        val = min(val, max_value)
        if val < 0:
            raise ValueError(f'Error in field UnsignedField<{self.key}>, positive integers expected but "{val}" is received')
        return int(val).to_bytes(self.bytes, 'big', signed=False)

    def from_binary(self, binary):
        return int.from_bytes(binary[:self.bytes], 'big', signed=False)


FIELD_MAP = {
    'array': ArrayField,
    'bits': BitsField,
    'bool': BoolField,
    'char': CharField,
    'date': DateField,
    'datetime': DateTimeField,
    'flags': FlagsField,
    'float': FloatField,
    'id': IdField,
    'signed': SignedField,
    'string': StringField,
    'time': TimeField,
    'timestamp': TimestampField,
    'unsigned': UnsignedField,
}
