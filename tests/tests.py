import unittest

import datetime
import json
import yaml
from protobin import Protocol
from protobin.errors import InputError, FormatError
from protobin import ProtobinLoader

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
            'char2': {
                "header": "C2",
                "fields": {
                    'test': {'bytes': 2, 'type': 'char'},
                    'prueba': {'bytes': 2, 'type': 'char'}
                }
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
                "fields": {'test': {'bytes': 4, 'type': 'float', 'decimals': 6}}
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
            'timestamp6': {
                "header": "T6",
                "fields": {'test': {'bytes': 6, "decimals": 3, 'type': 'timestamp'}}
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

    def test_array_none(self):
        data = {}
        with self.assertRaises(ValueError):
            self.protocol.encode(data, 'array')

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

    def test_char_utf(self):
        data = {'test': 'ñ'}
        binary = self.protocol.encode(data, 'char')
        print('binary', binary)
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_char2(self):
        data = {'test': 'FA', 'prueba': 'DO'}
        binary = self.protocol.encode(data, 'char2')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)
        data = {'test': '', 'prueba': 'F'}
        binary = self.protocol.encode(data, 'char2')
        print(binary)
        h, recv = self.protocol.decode(binary)
        data_corregida = {'test': '  ', 'prueba': 'F '}
        self.assertEqual(data_corregida, recv)
        print(recv)

    def test_char2_utf(self):
        data = {'test': 'FA', 'prueba': 'ÑA'}
        binary = self.protocol.encode(data, 'char2')
        h, recv = self.protocol.decode(binary)
        data['prueba'] = 'Ñ'
        self.assertEqual(data, recv)
        data = {'test': '', 'prueba': 'SÍ'}
        binary = self.protocol.encode(data, 'char2')
        print(binary)
        h, recv = self.protocol.decode(binary)
        data['prueba'] ='S '
        data['test'] ='  '
        self.assertEqual(data, recv)
        print(recv)
        data = {'test': 'ÉL', 'prueba': 'NO'}
        binary = self.protocol.encode(data, 'char2')
        print(binary)
        h, recv = self.protocol.decode(binary)
        data['test'] ='É'
        self.assertEqual(data, recv)
        print(recv)



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
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)
        data = {'test': 0}
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

        protocol = Protocol(js={'formats': {
            'unsigned': {
                "header": "u",
                "fields": {
                    "geofence": {"bytes": 2, "type": "unsigned"},
                    "orden": {"bytes": 1, "type": "unsigned"},
                    "delta": {"bytes": 1, "type": "unsigned"},
                    "origin": {"bytes": 2, "type": "unsigned"},
                    "id": {"bytes": 0, "type": "string"}
                }
            }
        }})
        data = {
            "id": "11",
            "orden": 0,
            "origin": 57,
            "delta": 5,
            "geofence": 200
        }
        binary = protocol.encode(data, 'unsigned')
        print(binary)
        h, recv = protocol.decode(binary)
        print(recv)
        self.assertEqual(data, recv)

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
        data = {'test': 'ñandú'}
        binary = self.protocol.encode(data, 'string')
        h, recv = self.protocol.decode(binary)
        print('binary', binary)
        self.assertEqual(data, recv)

    def test_timestamp(self):
        data = {'test': datetime.datetime(2024, 9, 13, 15, 23, 51, 265981)}
        binary = self.protocol.encode(data, 'timestamp')
        h, recv = self.protocol.decode(binary)
        self.assertEqual(data, recv)

    def test_timestamp6(self):
        data = {'test': datetime.datetime(2025, 1, 24, 9, 18, 24, 896000)}
        binary = self.protocol.encode(data, 'timestamp6')
        print(binary)
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
            'schedule': None
        }
        binary = server.encode(data, 'login')
        print(f'server ({len(binary)})', binary)
        header, recv = client.decode(binary)
        self.assertEqual(header, 'login')
        self.assertEqual(data, recv)

    def test_login_binary(self):
        client = Protocol(file='demo.json', server=False)
        binary = b'T=\x00\n\x00\x03\x03\x00\x00\x00T\x00\x00\x0b\x8a\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
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

    def test_position_binary(self):
        data = {'positions':
                    [{'time': datetime.datetime(2024, 10, 18, 15, 57, 38),
                      'lng': -77.015533, 'lat': -12.061365, 'speed': 105, 'mark': None, 'busstop': None}],
                'sales': 0, 'events': [], 'direction': None, 'route': None, 'state': None, 'trip': None
                }
        client = Protocol(file='demo.json', server=False)
        binary = client.encode(data, 'report')
        binary2 = b'PV=\x01\x18\x10$\x15W8\xfbh\xd6\x13\xffG\xf5Ki\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00'
        self.assertEqual(binary, binary2)
        server = Protocol(file='demo.json', server=True)
        header, recv = server.decode(binary)
        self.assertEqual(recv, data)

    def test_teltonika_position_hex(self):
        hexdata = '000000000000003608010000016B40D8EA30010000000000000000000000000000000105021503010101425E0F01F10000601A014E0000000000000000010000C7CF'
        binary = bytes.fromhex(hexdata)
        client = Protocol(file='codec8.json', server=None)
        header, recv = client.decode(binary)
        self.assertEqual(recv, {
            'positions': [{
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
                ]}
            ],
            '#reports': 1
        })

    def test_login_keyerror(self):
        client = Protocol(file='demo.json', server=False)
        data = {}
        with self.assertRaises(InputError):
            client.encode(data, 'not_exist')

    def test_no_crc(self):
        data = {'serial': '359769037211486'}
        client = Protocol(file='codec8.json')
        binary = client.encode(data, 'login')
        self.assertEqual(b'\x00\x0f359769037211486', binary)
        recv = client.decode(binary, 'login')
        self.assertEqual(data, recv)

    def test_crc(self):
        data = {'positions': [{'time': datetime.datetime(2024, 10, 19, 9, 37, 57, 555000), 'priority': 1, 'lng': -77.0155334, 'lat': -12.0613651, 'alt': 0, 'angle': 0, 'satellites': 3, 'speed': 105, 'event_io': 0, '#events': 0, 'events1b': [], 'events2b': [], 'events4b': [], 'events8b': []}], '#reports': 1}
        client = Protocol(file='codec8.json')
        binary = client.encode(data, 'report')
        self.assertEqual(b'\x00\x00\x00\x00\x00\x00\x00!\x08\x01\x00\x00\x01\x92\xa56\xaf\xb3\x01\xd2\x18\\\xba\xf8\xcf\x94\xed\x00\x00\x00\x00\x03\x00i\x00\x00\x00\x00\x00\x00\x01\x00\x00\xa3\xe4', binary)
        header, recv = client.decode(binary)
        self.assertEqual(data, recv)

    def test_status_crc(self):
        data = {'status': 'E', 'direction': 'A', 'next_next_control': '', 'next_next_time': '     ', 'next_control': '', 'next_time': '     ', 'previous_control': '', 'delay': 0, 'front_control': '', 'back_control': '', 'back_back_control': '', 'datero_bus_-1': 0, 'datero_dif_-1': 0, 'datero_bus_0': 0, 'datero_dif_0': 0, 'datero_bus_1': 0, 'datero_dif_1': 0, 'datero_bus_2': 0, 'datero_dif_2': 0, 'datero_bus_3': 256, 'datero_dif_3': 0, 'datero_bus_4': 0, 'datero_dif_4': 0, 'datero_bus_5': 0, 'datero_dif_5': 0}
        client = Protocol(file='codec8.json')
        binary = client.encode(data, 'status3')
        self.assertEqual(b's=EA\x00     \x00     \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\xb6\xd6', binary)
        header, recv = client.decode(binary)
        self.assertEqual(data, recv)

    def test_unheader(self):
        protocol = Protocol(js={'formats': {'report_ack': {
             'fields': {
                'positions': {'bytes': 4, 'type': 'unsigned'}
             }}}})
        data = {'positions': 1}
        binary = protocol.encode(data, 'report_ack')
        self.assertEqual(binary, b'\x00\x00\x00\x01')

    def test_decode_codec8(self):
        # binary = b'\xfe\x0f350424068858891\x00\x00\x01\x06CBF541\x04\x00\x02R\x00\x00\x00\x00\x01\x00\x00\x1e\n\x04\x00)\x11$\x100\x00R\xff\x00\x00\x00\x02'
        # binary = b'\x00\x00\x00\x00\x00\x00\x01\x11\x08\t\x00\x00\x01\x93x\xd74\xf0\x00\xd2\x15\x19\xe6\xf8\xc6\xe8\x9e\x00Z\x01b\x0e\x00\r\x00\x00\x00\x00\x00\x00\x00\x00\x01\x93x\xd7_\xe8\x00\xd2\x15\x1b#\xf8\xc6\xfau\x00W\x00\x06\x0f\x00\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x01\x93x\xd7\x86\xf8\x00\xd2\x15\x19\xf7\xf8\xc7\x0c~\x00S\x01e\x10\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x01\x93x\xd7\xd5\x18\x00\xd2\x15\x19\xf7\xf8\xc7\x14=\x00U\x00\x02\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x93x\xd8#8\x00\xd2\x15\x19\xf7\xf8\xc7\x14=\x00U\x00\x02\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x93x\xd8qX\x00\xd2\x15\x19\xf7\xf8\xc7\x14=\x00U\x00\x02\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x93x\xd8\xb3\xc0\x00\xd2\x15\x1bU\xf8\xc7%\xe2\x00R\x01g\x10\x00\x19\x00\x00\x00\x00\x00\x00\x00\x00\x01\x93x\xd8\xcf\x18\x00\xd2\x15\x1a\xe0\xf8\xc79\x8b\x00T\x01g\x0f\x00\x17\x00\x00\x00\x00\x00\x00\x00\x00\x01\x93x\xd8\xeeX\x00\xd2\x15\x1al\xf8\xc7K\x1f\x00Y\x00\x01\x0e\x00\x17\x00\x00\x00\x00\x00\x00\t\x00\x00\x13x'
        binary = b'\x00\x00\x00\x00\x00\x00\x00!\x08\x01\x00\x00\x01\x93\x92\x82\xb5\xa0\x00\xd2\x1bB\x12\xf8\xcb\xbf[\x00\xc2\x01\n\x10\x00\x0c\x00\x00\x00\x00\x00\x00\x01\x00\x00=G'
        client = Protocol(file='codec8.json')
        header, recv = client.decode(binary)
        print(header, recv)

    def test_decode_sergio(self):
        val = {'id': '675882972c030d7f86188ee9', 'command': 'C', 'value': 'value'}
        client = Protocol(js={"formats": {"command": {
            "header": "$",
            "server": {
                "comando": {"bytes": 1, "type": "char"},
                "id": {"bytes": 0, "type": "string"},
                "value": {"bytes": 0, "type": "string"}
            },
            "client": {
                "id": {"bytes": 0, "type": "string"}
            }
        }}}, server=True)
        binary = client.encode(val, 'command')
        print(binary)

    def test_singleton(self):
        protocol1 = ProtobinLoader('codec8.json')
        protocol2 = ProtobinLoader('codec8.json')
        protocol3 = ProtobinLoader('codec8.json')
        protocol4 = ProtobinLoader('codec8.json')
        protocol5 = ProtobinLoader('demo.json', server=False)
        protocol6 = ProtobinLoader('demo.json', server=True)
        protocol7 = ProtobinLoader('demo.json', server=True)
        protocol8 = ProtobinLoader('demo.json', server=True)

    def test_error_type(self):
        with self.assertRaises(FormatError):
            Protocol(js={"formats": {"command": {
                "header": "$",
                "server": {
                    "comando": {"bytes": 1, "type": "char"},
                    "id": {"bytes": 0, "type": "string"},
                    "value": {"bytes": 0, "type": "string"}
                },
                "client": {
                    "id": {"bytes": 0}
                }
            }}}, server=True)

    def test_teltonika_binary(self):
        binary = b'\x00\x00\x00\x00\x00\x00\x00!\x08\x01\x00\x00\x01\x94\xd26B\xd8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xa4\x12'
        client = Protocol(file='teltonika.json', server=None)
        header, recv = client.decode(binary)
        print(recv)

    def test_status_teltonika(self):
        pesquero = b'S=RA\x07IQUITOS14:05\x06LOBATO\x04\x07IGLESIA\x00f\x08\x00n\x05\x00\x96\x03\x01m\x08\x00\xb5\r\x01w\t\x00\x00o\xb4'
        client = Protocol(file='teltonika.json', server=None)
        header, recv = client.decode(pesquero)
        print(recv)
        binary = client.encode(recv, header)
        print(binary)
        self.assertEqual(pesquero, binary)

    def test_teltonika_login_hex(self):
        hexdata = '000F333536333037303432343431303133'
        binary = bytes.fromhex(hexdata)
        client = Protocol(file='codec8.json', server=None)
        recv = client.decode(binary, 'login')
        self.assertEqual(recv, {'serial': '356307042441013'})
        binary2 = client.encode(recv, 'login')
        self.assertEqual(binary, binary2)
        print(binary2)

    def test_teltonika_login(self):
        client = Protocol(file='codec8.json', server=None)
        data = {'padron': '110', 'company': 'roma', 'route': 'IO37'}
        binary = client.encode(data, 'login_status')
        print(binary)
        self.assertEqual(b'P=\x03110\x04roma\x04IO37\x19\x8f', binary)

    def test_teltonika_login_urbanito(self):
        client = Protocol(file='codec8.json', server=None)
        data = {'company': 'urbanito', 'route': '9802'}
        binary = client.encode(data, 'login_status')
        print(binary)
        self.assertEqual(b'P=\x00\x08urbanito\x049802+\xbf', binary)

    def test_message_teltonika(self):
        data = {'text': 'prueba de mensaje'}
        client = Protocol(file='teltonika.json', server=None)
        binary = client.encode(data, 'message')
        print(binary)
        self.assertEqual(binary, b'M=\x11prueba de mensaje48')

    def test_history_geofence_ms(self):
        codec = {
            "formats":{
                "history_geofence_ms": {
                    "header": "$",
                    "fields": {
                        "items": {
                            "type": "array",
                            "array": {
                                "id": {"bytes": 2, "type": "unsigned"},
                                "orden" : {"bytes": 1, "type": "unsigned"},
                                "longitud": {"bytes": 4, "type": "float", "decimals": 6},
                                "latitud": {"bytes": 4, "type": "float", "decimals": 6},
                                "radio": {"bytes": 2, "type": "unsigned"},
                                "ruta": {"bytes": 1, "type": "unsigned"},
                                "lado,control,datear,activo": {"type": "flags"},
                                "nombre": {"bytes": 15, "type": "char"},
                                "timestamp":{"bytes": 6, "decimals": 3, "type": "timestamp"},
                                "type": {"bytes": 1, "type": "char"}
                            }
                        },
                        "next": {"bytes": 1, "type": "char"}
                    }
                }
            }
        }
        data = {'items': [{'id': 2, 'lado': False, 'ruta': 2, 'audio': 'HU', 'orden': 8, 'radio': 70, 'activo': True, 'datear': True, 'nombre': 'FINAL', 'control': True, 'latitud': -12.0627343, 'retorno': True, 'sagrado': False, 'longitud': -77.0153672, 'terminal': True, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 486000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}, {'id': 5, 'lado': False, 'ruta': 2, 'audio': 'UN', 'orden': 2, 'radio': 70, 'activo': True, 'datear': True, 'nombre': 'UNIVERITARIA', 'control': True, 'latitud': -12.0500755, 'retorno': False, 'sagrado': False, 'longitud': -77.0772618, 'terminal': False, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 518000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}, {'id': 6, 'lado': False, 'ruta': 2, 'audio': 'CA', 'orden': 3, 'radio': 70, 'activo': True, 'datear': True, 'nombre': 'CARCAMO', 'control': True, 'latitud': -12.0472635, 'retorno': False, 'sagrado': False, 'longitud': -77.0508689, 'terminal': False, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 528000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}, {'id': 7, 'lado': False, 'ruta': 2, 'audio': '2 ', 'orden': 4, 'radio': 70, 'activo': True, 'datear': True, 'nombre': '2 DE MAYO', 'control': True, 'latitud': -12.0465238, 'retorno': False, 'sagrado': False, 'longitud': -77.043466, 'terminal': False, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 536000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}, {'id': 8, 'lado': False, 'ruta': 2, 'audio': 'PL', 'orden': 5, 'radio': 70, 'activo': True, 'datear': True, 'nombre': 'PLAZA SAN MARTIN', 'control': True, 'latitud': -12.0511405, 'retorno': False, 'sagrado': False, 'longitud': -77.0355159, 'terminal': False, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 544000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}, {'id': 13, 'lado': True, 'ruta': 2, 'audio': 'AB', 'orden': 4, 'radio': 70, 'activo': True, 'datear': True, 'nombre': 'ABANCAY', 'control': True, 'latitud': -12.0547289, 'retorno': False, 'sagrado': False, 'longitud': -77.0298779, 'terminal': False, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 585000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}, {'id': 14, 'lado': True, 'ruta': 2, 'audio': 'PL', 'orden': 5, 'radio': 70, 'activo': True, 'datear': True, 'nombre': 'PLAZA SAN MARTIN', 'control': True, 'latitud': -12.0520219, 'retorno': False, 'sagrado': False, 'longitud': -77.0339656, 'terminal': False, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 593000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}, {'id': 15, 'lado': True, 'ruta': 2, 'audio': '2 ', 'orden': 6, 'radio': 70, 'activo': True, 'datear': True, 'nombre': '2 DE MAYO', 'control': True, 'latitud': -12.0467074, 'retorno': False, 'sagrado': False, 'longitud': -77.0421463, 'terminal': False, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 601000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}, {'id': 17, 'lado': True, 'ruta': 2, 'audio': 'TE', 'orden': 9, 'radio': 70, 'activo': True, 'datear': True, 'nombre': 'TERMINAL', 'control': True, 'latitud': -12.0492046, 'retorno': False, 'sagrado': False, 'longitud': -77.088908, 'terminal': True, 'timestamp': datetime.datetime(2020, 7, 27, 14, 12, 14, 618000), 'refrecuenciar': False, 'type': '+', 'tabla': 'G'}], 'next': 'P'}
        client = Protocol(js=codec, server=None)
        binary = client.encode(data, 'history_geofence_ms')
        rasp = b'$=\t\x00\x02\x08\xfbh\xd6\xb9\xffG\xef\xf2\x00F\x02\x07FINAL          \x01s\x91\xb0\x90\x96+\x00\x05\x02\xfbg\xe4\xf2\xffH!d\x00F\x02\x07UNIVERITARIA   \x01s\x91\xb0\x90\xb6+\x00\x06\x03\xfbhL\x0b\xffH,`\x00F\x02\x07CARCAMO        \x01s\x91\xb0\x90\xc0+\x00\x07\x04\xfbhh\xf6\xffH/D\x00F\x02\x072 DE MAYO      \x01s\x91\xb0\x90\xc8+\x00\x08\x05\xfbh\x88\x04\xffH\x1d<\x00F\x02\x07PLAZA SAN MARTI\x01s\x91\xb0\x90\xd0+\x00\r\x04\xfbh\x9e\n\xffH\x0f7\x00F\x02\x0fABANCAY        \x01s\x91\xb0\x90\xf9+\x00\x0e\x05\xfbh\x8e\x12\xffH\x19\xca\x00F\x02\x0fPLAZA SAN MARTI\x01s\x91\xb0\x91\x01+\x00\x0f\x06\xfbhn\x1e\xffH.\x8d\x00F\x02\x0f2 DE MAYO      \x01s\x91\xb0\x91\t+\x00\x11\t\xfbg\xb7t\xffH$\xcb\x00F\x02\x0fTERMINAL       \x01s\x91\xb0\x91\x1a+P'
        self.assertEqual(binary, rasp)
        h, recv = client.decode(binary)
        print(recv)
