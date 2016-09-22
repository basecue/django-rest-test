import unittest


class DecoratorsTestCase(unittest.TestCase):
    def test_anonymous_decorator(self):

        from rest_tests import RestTests

        @RestTests.anonymous_user.can_create
        class DecoratedTests(RestTests):
            pass

        self.assertEqual(DecoratedTests.anonymous_user.allowed_operations, {'create'})

    def test_multiple_anonymous_decorators(self):

        from rest_tests import RestTests

        @RestTests.anonymous_user.can_create
        @RestTests.anonymous_user.can_retrieve
        class DecoratedTests(RestTests):
            pass

        self.assertEqual(DecoratedTests.anonymous_user.allowed_operations, {'create', 'retrieve'})

    def test_inheritance_decorator(self):
        from rest_tests import RestTests

        class MyTests(RestTests):
            pass

        @MyTests.anonymous_user.can_create
        class DecoratedTests(RestTests):
            pass

        self.assertEqual(MyTests.anonymous_user.allowed_operations, set())
        self.assertEqual(DecoratedTests.anonymous_user.allowed_operations, {'create'})

    def test_strange_inheritance_decorator(self):
        from rest_tests import RestTests

        class MyTests(RestTests):
            pass

        @RestTests.anonymous_user.can_create
        class DecoratedTests(MyTests):
            pass

        self.assertEqual(MyTests.anonymous_user.allowed_operations, set())
        self.assertEqual(DecoratedTests.anonymous_user.allowed_operations, {'create'})


if __name__ == '__main__':
    unittest.main()
