import unittest


class BasicTestCase(unittest.TestCase):
    def _dir_tests(self, cls):
        return [name for name in dir(cls) if name.startswith('test_')]

    def test_anonymous(self):
        from rest_test import RestTest

        class AnonymousTest(RestTest):
            pass

        self.assertCountEqual(
            self._dir_tests(AnonymousTest),
            [
                'test_create_by_anonymous_user',
                'test_retrieve_by_anonymous_user',
                'test_update_by_anonymous_user',
                'test_delete_by_anonymous_user',
                'test_patch_by_anonymous_user',
                'test_list_by_anonymous_user'
            ]
        )

    def test_user(self):
        from rest_test import RestTest, RestUser

        class UserTest(RestTest):
            another_user = RestUser

        self.assertCountEqual(
            self._dir_tests(UserTest),
            [
                'test_create_by_anonymous_user',
                'test_retrieve_by_anonymous_user',
                'test_update_by_anonymous_user',
                'test_delete_by_anonymous_user',
                'test_patch_by_anonymous_user',
                'test_list_by_anonymous_user',

                'test_create_by_another_user',
                'test_retrieve_by_another_user',
                'test_update_by_another_user',
                'test_delete_by_another_user',
                'test_patch_by_another_user',
                'test_list_by_another_user'
            ]
        )

    def test_user_inheritance(self):
        from rest_test import RestTest, RestUser

        class UserTest(RestTest):
            another_user = RestUser

        class InheritedUserTest(UserTest):
            another_user_2 = RestUser

        self.assertCountEqual(
            self._dir_tests(InheritedUserTest),
            [
                'test_create_by_anonymous_user',
                'test_retrieve_by_anonymous_user',
                'test_update_by_anonymous_user',
                'test_delete_by_anonymous_user',
                'test_patch_by_anonymous_user',
                'test_list_by_anonymous_user',

                'test_create_by_another_user',
                'test_retrieve_by_another_user',
                'test_update_by_another_user',
                'test_delete_by_another_user',
                'test_patch_by_another_user',
                'test_list_by_another_user',

                'test_create_by_another_user_2',
                'test_retrieve_by_another_user_2',
                'test_update_by_another_user_2',
                'test_delete_by_another_user_2',
                'test_patch_by_another_user_2',
                'test_list_by_another_user_2'
            ]
        )

    def test_user_inheritance_override(self):
        from rest_test import RestTest, RestUser

        class UserTest(RestTest):
            another_user = RestUser

        class InheritedUserTest(UserTest):
            another_user = RestUser

        self.assertCountEqual(
            self._dir_tests(InheritedUserTest),
            [
                'test_create_by_anonymous_user',
                'test_retrieve_by_anonymous_user',
                'test_update_by_anonymous_user',
                'test_delete_by_anonymous_user',
                'test_patch_by_anonymous_user',
                'test_list_by_anonymous_user',

                'test_create_by_another_user',
                'test_retrieve_by_another_user',
                'test_update_by_another_user',
                'test_delete_by_another_user',
                'test_patch_by_another_user',
                'test_list_by_another_user'
            ]
        )

if __name__ == '__main__':
    unittest.main()
