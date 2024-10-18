import unittest

import datetime
import json
import yaml
from protobin import Protocol
from protobin.errors import InputError, FormatError

DATA = {
        'positions': [
            {
                'time': datetime.datetime(2024, 1, 1, 8, 0, 0),
                'lng': -11.485014,
                'lat': -77.621845,
                'speed': 20,
                'mark': None,
                'busstop': 16
            },
            {
                'time': datetime.datetime(2024, 1, 1, 8, 0, 5),
                'lng': -11.485414,
                'lat': -77.622245,
                'speed': 25,
                'mark': None,
                'busstop': 16
            },
            {
                'time': datetime.datetime(2024, 1, 1, 8, 0, 10),
                'lng': -11.485514,
                'lat': -77.621945,
                'speed': 18,
                'mark': None,
                'busstop': 16
            },
            {
                'time': datetime.datetime(2024, 1, 1, 8, 0, 15),
                'lng': -11.485914,
                'lat': -77.622051,
                'speed': 35,
                'mark': 8,
                'busstop': 17
            },
            {
                'time': datetime.datetime(2024, 1, 1, 8, 0, 20),
                'lng': -11.486014,
                'lat': -77.622845,
                'speed': 1,
                'mark': 8,
                'busstop': 17
            },
        ],
        'trip': 259854,
        'route': 2,
        'direction': False,
        'state': 'R',
        'sales': 5850,
        'events': [
            {
                'id': 6,
                'value': 1
            }
        ]
    }


class BasicTest(unittest.TestCase):

    def setUp(self):
        self.protocol = Protocol(js={'formats': {
            'array': {
                "header": "A",
                "fields": {
                    'test': {'bytes': 0, 'type': 'array', 'array': {
                        'test': {'bytes': 0, 'type': 'string'}
                    }}}
            },
            'bits': {
                "header": "B",
                "fields": {'test': {'type': 'bits'}}
            },
            'bits_fixed': {
                "header": "b",
                "fields": {'test': {'type': 'bits', 'length': 7}}
            },
            'bool': {
                "header": "BO",
                "fields": {'test': {'bytes': 1, 'type': 'bool'}}
            },
            'char': {
                "header": "C",
                "fields": {'test': {'bytes': 1, 'type': 'char'}}
            },
            'date': {
                "header": "D",
                "fields": {'test': {'bytes': 1, 'type': 'date'}}
            },
            'datetime': {
                "header": "d",
                "fields": {'test': {'bytes': 1, 'type': 'datetime'}}
            },
            'flags': {
                "header": "F",
                "fields": {'f1,f2,f3,f4': {'type': 'flags'}}
            },
            'float': {
                "header": "f",
                "fields": {'test': {'bytes': 4, 'decimals': 6, 'type': 'float'}}
            },
            'id': {
                "header": "i",
                "fields": {'test': {'bytes': 4, 'type': 'id'}}
            },
            'signed': {
                "header": "+",
                "fields": {'test': {'bytes': 2, 'type': 'signed'}}
            },
            'string': {
                "header": "S",
                "fields": {'test': {'bytes': 0, 'type': 'string'}}
            },
            'time': {
                "header": "T",
                "fields": {'test': {'bytes': 2, 'type': 'time'}}
            },
            'timestamp': {
                "header": "TS",
                "fields": {'test': {'bytes': 8, 'type': 'timestamp'}}
            },
            'unsigned': {
                "header": "u",
                "fields": {'test': {'bytes': 3, 'type': 'unsigned'}}
            }
        }})

    def test_array(self):
        data = {'test': [
            {'test': 'texto de prueba'},
            {'test': 'segunda prueba'},
            {'test': 'otra más'}]
        }
        binary = self.protocol.encode(data, 'array')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)
        data = {'test': [
            {'test': 'texto2 de prueba'},
            {'test': 'segunda prueba4'},
            {'test': 'otra más3'},
            {'test': 'y una última'}]
        }
        binary = self.protocol.encode(data, 'array')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_bits(self):
        data = {'test': [True, False, True, False, False] * 3}
        binary = self.protocol.encode(data, 'bits')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)
        data = {'test': [True, False, True, False, False] * 5}
        binary = self.protocol.encode(data, 'bits')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_bits_fixed(self):
        data = {'test': [True, False, True, False, False, True, True]}
        binary = self.protocol.encode(data, 'bits_fixed')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_bool(self):
        data = {'test': False}
        binary = self.protocol.encode(data, 'bool')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_bool_none(self):
        data = {'test': None}
        binary = self.protocol.encode(data, 'bool')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_char(self):
        data = {'test': 'F'}
        binary = self.protocol.encode(data, 'char')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_date(self):
        data = {'test': datetime.date(2024, 9, 13)}
        binary = self.protocol.encode(data, 'date')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_datetime(self):
        data = {'test': datetime.datetime(2024, 9, 13, 15, 23, 51)}
        binary = self.protocol.encode(data, 'datetime')
        print('binary', binary)
        h, recv = self.protocol.decode(binary)
        print('recv', recv)
        self.assertEqual(data, recv)

    def test_datetime_error_type(self):
        data = {'test': []}
        with self.assertRaises(ValueError) as er:
            self.protocol.encode(data, 'datetime')

    def test_datetime_none(self):
        data = {'test': None}
        binary = self.protocol.encode(data, 'datetime')
        print('binary', binary)
        h, recv = self.protocol.decode(binary)
        print('recv', recv)
        self.assertEqual(None, recv['test'])

    def test_time(self):
        data = {'test': datetime.time(15, 23)}
        binary = self.protocol.encode(data, 'time')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_time_none(self):
        data = {'test': None}
        binary = self.protocol.encode(data, 'time')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_flags(self):
        data = {'f1': True, 'f2': False, 'f3': False, 'f4': True}
        binary = self.protocol.encode(data, 'flags')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_flags_none(self):
        data = {'f1': True, 'f2': False, 'f3': False, 'f4': None}
        with self.assertRaises(ValueError):
            self.protocol.encode(data, 'flags')

    def test_flags_incomplete(self):
        data = {'f1': True, 'f2': False, 'f3': False}
        with self.assertRaises(ValueError):
            self.protocol.encode(data, 'flags')

    def test_float(self):
        data = {'test': -11.659812}
        binary = self.protocol.encode(data, 'float')
        print(binary)
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_signed(self):
        data = {'test': -11812}
        binary = self.protocol.encode(data, 'signed')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_unsigned(self):
        data = {'test': 9811812}
        binary = self.protocol.encode(data, 'unsigned')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_unsigned_zero(self):
        data = {'test': None}
        with self.assertRaises(ValueError) as er:
            self.protocol.encode(data, 'unsigned')

    def test_id(self):
        data = {'test': 254}
        binary = self.protocol.encode(data, 'id')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_id_zero(self):
        data = {'test': None}
        binary = self.protocol.encode(data, 'id')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_string(self):
        data = {'test': 'texto de prueba'}
        binary = self.protocol.encode(data, 'string')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)
        data = {'test': 'otro texto de prueba más largo'}
        binary = self.protocol.encode(data, 'string')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_timestamp(self):
        data = {'test': datetime.datetime(2024, 9, 13, 15, 23, 51, 265981)}
        binary = self.protocol.encode(data, 'timestamp')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_timestamp_null(self):
        data = {'test': None}
        binary = self.protocol.encode(data, 'timestamp')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)


class AdvancedTest(unittest.TestCase):

    def test_file_json(self):
        client = Protocol(file='demo.json', server=False)
        binary = client.encode(DATA, 'report')
        server = Protocol(file='demo.json', server=True)
        name, recv = server.decode(binary)
        self.assertEqual(DATA, recv)
        self.assertEqual(name, 'report')

    def test_json(self):
        protocol = Protocol(js={'formats': {'medida':
            {'header': 'M',
             'fields': {
                'id': {'bytes': 1, 'type': 'unsigned'},
                'nombre': {'type': 'string'},
                'valor': {'bytes': 2, 'type': 'signed'}
             }}}})
        data = {'id': 2, 'nombre': 'Voltaje', 'valor': -20}
        binary = protocol.encode(data, 'medida')
        h, recv = protocol.decode(binary)
        self.assertEqual(data, recv)
        data = {'id': 4, 'nombre': 'Corriente', 'valor': 240}
        binary = protocol.encode(data, 'medida')
        h, recv = protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_new_yaml(self):
        ym = yaml.full_load("""
login:
  client:
    serial:
      type: string
  header: T
  server:
    bus_number:
      bytes: 2
      type: id
    direction:
      bytes: 1
      type: bool
    driver:
      bytes: 4
      type: id
    geofence:
      bytes: 2
      type: id
    id:
      bytes: 2
      type: id
    route:
      bytes: 1
      type: id
    state:
      bytes: 1
      type: char
    trip:
      bytes: 4
      type: id
report:
  client:
    direction:
      bytes: 1
      type: bool
    events:
      array:
        id:
          bytes: 2
          type: unsigned
        value:
          bytes: 1
          type: unsigned
      bytes: 3
      type: array
    positions:
      array:
        busstop:
          bytes: 2
          type: id
        lat:
          bytes: 4
          decimals: 6
          type: float
        lng:
          bytes: 4
          decimals: 6
          type: float
        mark:
          bytes: 2
          type: id
        speed:
          bytes: 1
          type: unsigned
        time:
          bytes: 6
          type: datetime
      bytes: 19
      type: array
    route:
      bytes: 1
      type: unsigned
    sales:
      bytes: 3
      type: unsigned
    state:
      bytes: 1
      type: char
    trip:
      bytes: 4
      type: unsigned
  header: P
  server:
    positions:
      bytes: 1
      type: unsigned
""")
        js = json.dumps(ym, indent=2)

    def test_convert_json_to_yaml(self):
        with open('demo.json', 'r') as f:
            js = json.loads(f.read())
        ym = yaml.dump(js)
        print(ym)

    def test_login(self):
        client = Protocol(file='demo.json', server=False)
        server = Protocol(file='demo.json', server=True)

        data = {'serial': '15984316545'}
        binary = client.encode(data, 'login')
        print('client', binary)
        header, recv = server.decode(binary)
        self.assertEqual(header, 'login')
        self.assertEqual(data, recv)
        data = {
            'id': 43,
            'bus_number': 18,
            'route': 2,
            'direction': True,
            'geofence': None,
            'state': 'R',
            'trip': 5681121,
            'driver': 1432,
            'order': 5,
            'logged': False,
            'data': None,
            'schedule': datetime.time(11, 15)
        }
        binary = server.encode(data, 'login')
        print('server', binary)
        header, recv = client.decode(binary)
        self.assertEqual(header, 'login')
        self.assertEqual(data, recv)

    def test_login_binary(self):
        client = Protocol(file='demo.json', server=False)
        binary = b'T=\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        header, recv = client.decode(binary)
        self.assertEqual(header, 'login')
        print('recv', recv)

    def test_file_yaml(self):
        client = Protocol(file='demo.yaml', server=False)
        server = Protocol(file='demo.yaml', server=True)
        data = {'serial': '15984316545'}
        binary = client.encode(data, 'login')
        header, recv = server.decode(binary)
        self.assertEqual(header, 'login')
        self.assertEqual(data, recv)
        data = {
            'id': 61,
            'bus_number': 99,
            'route': 4,
            'direction': True,
            'geofence': None,
            'state': 'T',
            'trip': 2380,
            'driver': None,
            'order': 1,
            'logged': False,
            'data': None,
            'schedule': datetime.time(10, 15)
        }
        binary = server.encode(data, 'login')
        header, recv = client.decode(binary)
        self.assertEqual(header, 'login')
        self.assertEqual(data, recv)

    def test_file_json_yaml(self):
        client = Protocol(file='demo.json', server=False)
        server = Protocol(file='demo.yaml', server=True)
        data = {'serial': '15984316545'}
        binary = client.encode(data, 'login')
        header, recv = server.decode(binary)
        self.assertEqual(header, 'login')
        self.assertEqual(data, recv)
        data = {
            'id': 43,
            'bus_number': 18,
            'route': 2,
            'direction': True,
            'geofence': None,
            'state': 'R',
            'trip': 5681121,
            'driver': 1432,
            'order':21,
            'logged': True,
            'data': datetime.datetime(2010, 11, 22, 23, 15, 32),
            'schedule': None
        }
        binary = server.encode(data, 'login')
        header, recv = client.decode(binary)
        self.assertEqual(header, 'login')
        self.assertEqual(data, recv)

    def test_error_header(self):
        with self.assertRaises(FormatError):
            Protocol(js={
                'formats':
                    {'array': {
                        "header": "A",
                        "fields": {
                            'test': {'bytes': 0, 'type': 'array', 'array': {
                                'test': {'bytes': 0, 'type': 'string'}
                            }}}
                    },
                        'bits': {
                            "header": "B",
                            "fields": {'test': {'type': 'bits'}}
                        },
                        'bits_fixed': {
                            "header": "B",
                            "fields": {'test': {'type': 'bits', 'length': 7}}
                        }}
            })

    def test_teltonika_login(self):
        hexdata = '000F333536333037303432343431303133'
        binary = bytes.fromhex(hexdata)
        client = Protocol(file='codec8.json', server=None)
        recv = client.decode(binary, 'login')
        self.assertEqual(recv, {'serial': '356307042441013'})
        binary2 = client.encode(recv, 'login')
        self.assertEqual(binary, binary2)


    def test_teltonika_position(self):
        hexdata = '000000000000003608010000016B40D8EA30010000000000000000000000000000000105021503010101425E0F01F10000601A014E0000000000000000010000C7CF'
        binary = bytes.fromhex(hexdata)
        client = Protocol(file='codec8.json', server=None)
        length = int.from_bytes(binary[4:8], 'big', signed=False)
        clean_binary = binary[9:length + 9]
        crc16 = int.from_bytes(binary[length + 8: length + 12], client.crc_byteorder, signed=False)
        print('trama', binary[8:length + 8], 'crc', binary[length + 8: length + 12])
        self.assertEqual(crc16, client.get_crc(binary[8:length + 8]))
        recv = client.decode(clean_binary, 'reports')
        self.assertEqual(recv, {'reports': [{
            'time': datetime.datetime(2019, 6, 10, 5, 4, 46),
            'priority': 1,
            'lng': 0.0,
            'lat': 0.0,
            'alt': 0,
            'angle': 0,
            'satellites': 0,
            'speed': 0,
            'event_io': 1,
            '#events': 5,
            'events1b': [
                {'id': 21, 'value': 3},
                {'id': 1, 'value': 1}
            ],
            'events2b': [
                {'id': 66, 'value': 24079}
            ],
            'events4b': [
                {'id': 241, 'value': 24602}
            ],
            'events8b': [
                {'id': 78, 'value': 0}
            ],
            '#reports': 1,
        }]})

    def test_login_keyerror(self):
        client = Protocol(file='demo.json', server=False)
        data = {}
        client.encode(data, 'not_exist')
