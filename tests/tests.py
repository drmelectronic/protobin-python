import unittest

import datetime

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


class FormatTest(unittest.TestCase):

    def test_format_array(self):
        parser = Protocol(js={
            'array': [{'key': 'test', 'bytes': 0, 'type': 'array', 'array': [
                {'key': 'test', 'bytes': 0, 'type': 'string'}
            ]}]
        })

    def test_format_bits(self):
        parser = Protocol(js={
            'bits': [{'key': 'test', 'bytes': 2, 'type': 'bits'}],
        })

    def test_format_date(self):

        self.parser = Protocol(js={
            'date': [{'key': 'test', 'bytes': 1, 'type': 'date'}],
        })

    def test_format_flags(self):

        self.parser = Protocol(js={
            'flags': [{'keys': ['f1', 'f2', 'f3', 'f4'], 'bytes': 1, 'type': 'flags'}],
        })

    def test_format(self):

        self.parser = Protocol(js={
            'array': [{'key': 'test', 'bytes': 0, 'type': 'array', 'array': [
                {'key': 'test', 'bytes': 0, 'type': 'string'}
            ]}],
            'bits': [{'key': 'test', 'bytes': 2, 'type': 'bits'}],
            'bool': [{'key': 'test', 'bytes': 1, 'type': 'bool'}],
            'char': [{'key': 'test', 'bytes': 1, 'type': 'char'}],
            'date': [{'key': 'test', 'bytes': 3, 'type': 'date'}],
            'datetime': [{'key': 'test', 'bytes': 6, 'type': 'datetime'}],
            'flags': [{'keys': ['f1', 'f2', 'f3', 'f4'], 'bytes': 1, 'type': 'flags'}],
            'float': [{'key': 'test', 'bytes': 4, 'decimales': 6, 'type': 'float'}],
            'signed': [{'key': 'test', 'bytes': 2, 'type': 'signed'}],
            'string': [{'key': 'test', 'bytes': 0, 'type': 'string'}],
            'time': [{'key': 'test', 'bytes': 1, 'type': 'time'}],
            'timestamp': [{'key': 'test', 'bytes': 8, 'type': 'string'}],
            'unsigned': [{'key': 'test', 'bytes': 3, 'type': 'unsigned'}]
        })


class BasicTest(unittest.TestCase):

    def setUp(self):
        self.protocol = Protocol(js={
            'array': [{'key': 'test', 'bytes': 0, 'type': 'array', 'array': [
                {'key': 'test', 'bytes': 0, 'type': 'string'}
            ]}],
            'bits': [{'key': 'test', 'type': 'bits'}],
            'bool': [{'key': 'test', 'bytes': 1, 'type': 'bool'}],
            'char': [{'key': 'test', 'bytes': 1, 'type': 'char'}],
            'date': [{'key': 'test', 'bytes': 1, 'type': 'date'}],
            'datetime': [{'key': 'test', 'bytes': 1, 'type': 'datetime'}],
            'flags': [{'keys': ['f1', 'f2', 'f3', 'f4'], 'type': 'flags'}],
            'float': [{'key': 'test', 'bytes': 4, 'decimales': 6, 'type': 'float'}],
            'signed': [{'key': 'test', 'bytes': 2, 'type': 'signed'}],
            'string': [{'key': 'test', 'bytes': 0, 'type': 'string'}],
            'time': [{'key': 'test', 'bytes': 2, 'type': 'time'}],
            'timestamp': [{'key': 'test', 'bytes': 8, 'type': 'timestamp'}],
            'unsigned': [{'key': 'test', 'bytes': 3, 'type': 'unsigned'}]
        })

    def test_array(self):
        data = {'test': [
            {'test': 'texto de prueba'},
            {'test': 'segunda prueba'},
            {'test': 'otra más'}]
        }
        binary = self.protocol.encode(data, 'array')
        recv = self.protocol.decode(binary, 'array')
        self.assertEqual(data, recv)

    def test_bits(self):
        data = {'test': [True, False, True, False, False] * 3}
        print('data', data)
        binary = self.protocol.encode(data, 'bits')
        print('binary', binary)
        recv = self.protocol.decode(binary, 'bits')
        print('recv', recv)
        self.assertEqual(data, recv)

    def test_bool(self):
        data = {'test': False}
        binary = self.protocol.encode(data, 'bool')
        recv = self.protocol.decode(binary, 'bool')
        self.assertEqual(data, recv)

    def test_char(self):
        data = {'test': 'F'}
        binary = self.protocol.encode(data, 'char')
        recv = self.protocol.decode(binary, 'char')
        self.assertEqual(data, recv)

    def test_date(self):
        data = {'test': datetime.date(2024, 9, 13)}
        binary = self.protocol.encode(data, 'date')
        recv = self.protocol.decode(binary, 'date')
        self.assertEqual(data, recv)

    def test_datetime(self):
        data = {'test': datetime.datetime(2024, 9, 13, 15, 23, 51)}
        binary = self.protocol.encode(data, 'datetime')
        recv = self.protocol.decode(binary, 'datetime')
        self.assertEqual(data, recv)

    def test_time(self):
        data = {'test': datetime.time(15, 23)}
        binary = self.protocol.encode(data, 'time')
        recv = self.protocol.decode(binary, 'time')
        self.assertEqual(data, recv)

    def test_flags(self):
        data = {'f1': True, 'f2': False, 'f3': False, 'f4': True}
        binary = self.protocol.encode(data, 'flags')
        recv = self.protocol.decode(binary, 'flags')
        self.assertEqual(data, recv)

    def test_float(self):
        data = {'test': -11.659812}
        binary = self.protocol.encode(data, 'float')
        recv = self.protocol.decode(binary, 'float')
        self.assertEqual(data, recv)

    def test_signed(self):
        data = {'test': -11812}
        binary = self.protocol.encode(data, 'signed')
        recv = self.protocol.decode(binary, 'signed')
        self.assertEqual(data, recv)

    def test_unsigned(self):
        data = {'test': 9811812}
        binary = self.protocol.encode(data, 'unsigned')
        recv = self.protocol.decode(binary, 'unsigned')
        self.assertEqual(data, recv)

    def test_string(self):
        data = {'test': 'texto de prueba'}
        binary = self.protocol.encode(data, 'string')
        recv = self.protocol.decode(binary, 'string')
        self.assertEqual(data, recv)

    def test_timestamp(self):
        data = {'test': datetime.datetime(2024, 9, 13, 15, 23, 51, 265981)}
        binary = self.protocol.encode(data, 'timestamp')
        recv = self.protocol.decode(binary, 'timestamp')
        self.assertEqual(data, recv)


class AdvancedTest(unittest.TestCase):

    def test_file(self):
        protocol = Protocol(file='demo.json')
        binary = protocol.encode(DATA, 'report')
        recv = protocol.decode(binary, 'report')
        self.assertEqual(DATA, recv)

    def test_json(self):
        protocol = Protocol(js={'medida': [
                {'key': 'id', 'bytes': 1, 'type': 'unsigned'},
                {'key': 'nombre', 'type': 'string'},
                {'key': 'valor', 'bytes': 2, 'type': 'signed'}
            ]})
        data = {'id': 2, 'nombre': 'Voltaje', 'valor': -20}
        binary = protocol.encode(data, 'medida')
        print('binary', binary)
        recv = protocol.decode(binary, 'medida')
        print('recv', recv)
        self.assertEqual(data, recv)


