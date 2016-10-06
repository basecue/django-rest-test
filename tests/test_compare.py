import unittest
from rest_tests import compare


class BasicTestCase(unittest.TestCase):

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

        self.assertFalse(compare(data, expected_data))

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

        self.assertFalse(compare(data, expected_data))


class ItemEllipsisTestCase(unittest.TestCase):
    def test_basic(self):
        data = dict(
            a=1,
            b='2'
        )

        expected_data = dict(
            b='2',
            a=...
        )

        assert compare(data, expected_data)

    def test_basic_false(self):
        data = dict(
            a=1,
            b='2'
        )
        expected_data = dict(
            b=2,
            a=...
        )

        self.assertFalse(compare(data, expected_data))

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
                b=...,
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
                a=3,
                b=...,
                c=''
            )
        )

        self.assertFalse(compare(data, expected_data))

    def test_missing_basic_false(self):
        data = dict(
            a=1,
            b='2'
        )

        expected_data = dict(
            a=...
        )
        self.assertFalse(compare(data, expected_data))

    def test_moreover_basic_false(self):
        data = dict(
            a=1,
            b='2'
        )
        expected_data = dict(
            b=2,
            a=...,
            c='test'
        )

        self.assertFalse(compare(data, expected_data))

    def test_missing_deep_false(self):
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
                b=...,
            )
        )
        self.assertFalse(compare(data, expected_data))

    def test_moreover_deep_false(self):
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
                a=3,
                b=...,
                c='',
                d='test'
            )
        )

        self.assertFalse(compare(data, expected_data))


class CompleteEllipsisTestCase(unittest.TestCase):
    def test_basic(self):
        data = dict(
            a=1,
            b='2'
        )

        expected_data = {
            ...: ...
        }

        assert compare(data, expected_data)

    def test_basic_false(self):
        data = dict(
            a=1,
            b='2'
        )
        expected_data = {
            'b': 2,
            ...: ...
        }

        self.assertFalse(compare(data, expected_data))

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
            b={
                'a': 2,
                ...: ...,
                'c': ''
            }
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
            b={
                'a': 3,
                ...: ...,
                'c': ''
            }
        )

        self.assertFalse(compare(data, expected_data))

    def test_moreover_basic_false(self):
        data = dict(
            a=1,
            b='2'
        )
        expected_data = {
            'b': 2,
            ...: ...,
            'c': 'test'
        }

        self.assertFalse(compare(data, expected_data))

    def test_missing_deep_false(self):
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
            b={
                'a': 2,
                ...: ...
            }
        )
        assert compare(data, expected_data)

    def test_moreover_deep_false(self):
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
            b={
                'a': 3,
                ...: ...,
                'c': '',
                'd': 'test'
            }
        )

        self.assertFalse(compare(data, expected_data))

if __name__ == '__main__':
    unittest.main()
