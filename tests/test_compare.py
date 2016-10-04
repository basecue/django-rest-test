import unittest
from rest_tests import compare


class BasicTestCitse(unittest.TestCase):

    def test_basic(self):
        data = dict(
            a=1,
            b='2'
        )
        expected_data = dict(
            b='2',
            a=1
        )

        assert compare(data, expected_data)

    def test_basic_false(self):
        data = dict(
            a=1,
            b='2'
        )
        expected_data = dict(
            b=2,
            a=1
        )

        with self.assertRaises(Exception):
            compare(data, expected_data)

    def test_deep(self):
        data = dict(
            a=1,
            b=dict(
                b=dict(
                    a='test'
                ),
                a=2,
                c=''
            )
        )
        expected_data = dict(
            a=1,
            b=dict(
                a=2,
                b=dict(
                    a='test'
                ),
                c=''
            )
        )
        assert compare(data, expected_data)

    def test_deep_false(self):
        data = dict(
            a=1,
            b=dict(
                b=dict(
                    a='test'
                ),
                a=2,
                c=''
            )
        )
        expected_data = dict(
            a=1,
            b=dict(
                a=2,
                b=dict(
                    b=1
                ),
                c=''
            )
        )
        assert compare(data, expected_data)

if __name__ == '__main__':
    unittest.main()
