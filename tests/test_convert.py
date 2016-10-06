import unittest
from rest_tests import convert_data
from collections import OrderedDict


class ConvertTestCase(unittest.TestCase):

    def test_list(self):
        data = [1, 2, 3, '2']
        output = [1, 2, 3, '2']
        assert convert_data(data) == output

    def test_dict(self):
        data = {'a': 1, 3: 2, '2': 'x'}
        output = {'a': 1, 3: 2, '2': 'x'}
        assert convert_data(data) == output

    def test_list_in_dict(self):
        data = {'a': 1, 3: [1, 2, 3, '2'], '2': 'x'}
        output = {'a': 1, 3: [1, 2, 3, '2'], '2': 'x'}
        assert convert_data(data) == output

    def test_dict_in_list(self):
        data = [1, 2, {'a': 1, 3: 2, '2': 'x'}, '2']
        output = [1, 2, {'a': 1, 3: 2, '2': 'x'}, '2']
        assert convert_data(data) == output

    def test_ordereddict(self):
        data = OrderedDict({'a': 1, 3: 2, '2': 'x'})
        output = {'a': 1, 3: 2, '2': 'x'}
        assert convert_data(data) == output

    def test_list_in_ordereddict(self):
        data = OrderedDict({'a': 1, 3: [1, 2, 3, '2'], '2': 'x'})
        output = {'a': 1, 3: [1, 2, 3, '2'], '2': 'x'}
        assert convert_data(data) == output

    def test_ordereddict_in_list(self):
        data = [1, 2, OrderedDict({'a': 1, 3: 2, '2': 'x'}), '2']
        output = [1, 2, {'a': 1, 3: 2, '2': 'x'}, '2']
        assert convert_data(data) == output

if __name__ == '__main__':
    unittest.main()
