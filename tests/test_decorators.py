import unittest


class DecoratorsTestCase(unittest.TestCase):
    def test_anonymous_decorator(self):

        from rest_test import RestTest

        @RestTest.anonymous_user.can_create
        class DecoratedTest(RestTest):
            pass

        self.assertEqual(DecoratedTest.anonymous_user.allowed_operations, {'create'})

    def test_multiple_anonymous_decorators(self):

        from rest_test import RestTest

        @RestTest.anonymous_user.can_create
        @RestTest.anonymous_user.can_retrieve
        class DecoratedTest(RestTest):
            pass

        self.assertEqual(DecoratedTest.anonymous_user.allowed_operations, {'create', 'retrieve'})

    def test_same_class_decorator(self):

        from rest_test import RestTest, RestUser

        class DecoratedTest(RestTest):
            logged_user = RestUser

        DecoratedTest = DecoratedTest.logged_user.can_create(DecoratedTest)

        self.assertEqual(DecoratedTest.logged_user.allowed_operations, {'create'})

    def test_same_class_user(self):

        from rest_test import RestTest, RestUser

        class SimpleTest(RestTest):
            logged_user = RestUser(can_create=True)

        self.assertEqual(SimpleTest.logged_user.allowed_operations, {'create'})

    def test_same_class_user_inheritance(self):

        from rest_test import RestTest, RestUser

        class SimpleTest(RestTest):
            logged_user = RestUser(can_create=True)

        class InheritedTest(SimpleTest):
            pass

        self.assertEqual(InheritedTest.logged_user.allowed_operations, {'create'})

    def test_inheritance(self):

        from rest_test import RestTest, RestUser

        class SimpleTest(RestTest):
            logged_user = RestUser

        @SimpleTest.logged_user.can_create
        class InheritedTest(SimpleTest):
            pass

        class InheritedInheritedTest(InheritedTest):
            pass

        self.assertEqual(InheritedTest.logged_user.allowed_operations, {'create'})
        self.assertEqual(InheritedInheritedTest.logged_user.allowed_operations, set())

    # def test_inheritance_user(self):
    #     """
    #     not defined behavior
    #     """
    #     from rest_test import RestTest, RestUser
    #
    #     class SimpleTest(RestTest):
    #         logged_user = RestUser(can_list=True)
    #
    #     @SimpleTest.logged_user.can_create
    #     class InheritedTest(SimpleTest):
    #         pass
    #
    #     class InheritedInheritedTest(InheritedTest):
    #         pass
    #
    #     self.assertEqual(SimpleTest.logged_user.allowed_operations, {'list'})
    #     self.assertEqual(InheritedTest.logged_user.allowed_operations, {'list', 'create'})
    #     self.assertEqual(InheritedInheritedTest.logged_user.allowed_operations, {'list'})

    def test_decorated_all_users(self):
        from rest_test import RestTest, RestUser

        class MyTest(RestTest):
            logged_user = RestUser

        @RestTest.all_users.can_create
        class DecoratedTest(MyTest):
            pass

        self.assertEqual(DecoratedTest.anonymous_user.allowed_operations, {'create'})
        self.assertEqual(DecoratedTest.logged_user.allowed_operations, {'create'})

    def test_inheritance_decorator(self):
        from rest_test import RestTest

        class MyTest(RestTest):
            pass

        @MyTest.anonymous_user.can_create
        class DecoratedTest(RestTest):
            pass

        self.assertEqual(MyTest.anonymous_user.allowed_operations, set())
        self.assertEqual(DecoratedTest.anonymous_user.allowed_operations, {'create'})

    def test_strange_inheritance_decorator(self):
        from rest_test import RestTest

        class MyTest(RestTest):
            pass

        @RestTest.anonymous_user.can_create
        class DecoratedTest(MyTest):
            pass

        self.assertEqual(MyTest.anonymous_user.allowed_operations, set())
        self.assertEqual(DecoratedTest.anonymous_user.allowed_operations, {'create'})

if __name__ == '__main__':
    unittest.main()
