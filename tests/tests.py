import unittest

import datetime
import json
import yaml
from protobin import Protocol

DATA = {
        'positions': [
            {
                'time': datetime.datetime(2024, 1, 1, 8, 0, 0),
                'lng': -11.485014,
                'lat': -77.621845,
                'speed': 20,
                'mark': 0,
                'busstop': 16
            },
            {
                'time': datetime.datetime(2024, 1, 1, 8, 0, 5),
                'lng': -11.485414,
                'lat': -77.622245,
                'speed': 25,
                'mark': 0,
                'busstop': 16
            },
            {
                'time': datetime.datetime(2024, 1, 1, 8, 0, 10),
                'lng': -11.485514,
                'lat': -77.621945,
                'speed': 18,
                'mark': 0,
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
        self.protocol = Protocol(js={
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
        })

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
        self.assertEqual(datetime.datetime(2000, 1, 1), recv['test'])

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

    def test_float(self):
        data = {'test': -11.659812}
        binary = self.protocol.encode(data, 'float')
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


class AdvancedTest(unittest.TestCase):

    def test_file_json(self):
        protocol = Protocol(file='demo.json')
        binary = protocol.encode(DATA, 'report')
        h, recv = protocol.decode(binary)
        self.assertEqual(DATA, recv)
        self.assertEqual(h, 'P')

    # def test_file_yaml(self):
    #     protocol = Protocol(file='demo.yaml')
    #     binary = protocol.encode(DATA, 'report')
    #     h, recv = protocol.decode(binary)
    #     self.assertEqual(h, 'P')

    def test_json(self):
        protocol = Protocol(js={'medida':
            {'header': 'M',
             'fields': {
                'id': {'bytes': 1, 'type': 'unsigned'},
                'nombre': {'type': 'string'},
                'valor': {'bytes': 2, 'type': 'signed'}
             }}})
        data = {'id': 2, 'nombre': 'Voltaje', 'valor': -20}
        binary = protocol.encode(data, 'medida')
        h, recv = protocol.decode(binary)
        self.assertEqual(data, recv)
        data = {'id': 4, 'nombre': 'Corriente', 'valor': 240}
        binary = protocol.encode(data, 'medida')
        h, recv = protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_new_yaml(self):
        ym = yaml.full_load("""report:
  positions:
    bytes: 19
    type: array
    array:
      time:
        bytes: 6
        type: datetime
      lng:
        bytes: 4
        decimals: 6
        type: float
      lat:
        bytes: 4
        decimals: 6
        type: float
      speed:
        bytes: 1
        type: unsigned
      mark:
        bytes: 2
        type: unsigned
      busstop:
        bytes: 2
        type: unsigned
  trip:
    bytes: 4
    type: unsigned
  route:
    bytes: 1
    type: unsigned
  direction:
    bytes: 1
    type: bool
  state:
    bytes: 1
    type: char
  sales:
    bytes: 3
    type: unsigned
  events:
    bytes: 3
    type: array
    array:
      id:
        bytes: 2
        type: unsigned
      value:
        bytes: 1
        type: unsigned
""")
        js = json.dumps(ym, indent=2)

    def test_convert_json_to_yaml(self):
        protocol = Protocol(file='demo.json')

    def test_login(self):
        protocol = Protocol(file='demo.json')
        data = {'serial': '15984316545'}
        binary = protocol.encode(data, 'login')
        header, recv = protocol.decode(binary)
        self.assertEqual(data, recv)
        self.assertEqual(header, 'T')