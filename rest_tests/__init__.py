from functools import partial

from rest_framework import status
from rest_framework.test import APITestCase
from pprint import pprint
from collections import OrderedDict


class BaseAPITestCase(APITestCase):
    def _data_format(self, data):
        if isinstance(data, list):
            ret = []
            for item in data:
                if isinstance(item, OrderedDict):
                    ret.append(dict(item))
                else:
                    ret.append(item)
            return ret

        elif isinstance(data, OrderedDict):
            return dict(data)
        else:
            return data

    def _request(self, method, url, data=None):
        response = getattr(self.client, method)(url, data=data, format='json')
        pprint(dict(
            request=dict(
                method=method,
                url=url,
                input_data=data
            ),
            response=dict(
                status_code=response.status_code,
                output_data=self._data_format(response.data) if hasattr(response, 'data') else None
            )
        ))
        return response

    def _get(self, url, data=None):
        return self._request('get', url, data=data)

    def _post(self, url, data=None):
        return self._request('post', url, data=data)

    def _put(self, url, data=None):
        return self._request('put', url, data=data)

    def _delete(self, url, data=None):
        return self._request('delete', url, data=data)

    def _patch(self, url, data=None):
        return self._request('patch', url, data=data)

    # assert methods
    def assert_disabled(self, response):
        if response.status_code in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_403_FORBIDDEN
        ):
            return True
        elif response.status_code == status.HTTP_200_OK:
            if not hasattr(response, 'data') or response.data is None:
                return True
            else:
                return False
        else:
            return False

    def assert_equal(self, response, data):
        pprint(dict(expected=data))
        assert response.data == data

    url_list = ''
    url_detail = ''

    def create(self, input_data=None):
        return self._post(self.url_list, data=input_data)

    def retrieve(self, input_data=None):
        return self._get(self.url_detail, data=input_data)

    def update(self, input_data=None):
        return self._put(self.url_detail, data=input_data)

    def delete(self, input_data=None):
        return self._delete(self.url_detail, data=input_data)

    def list(self, input_data=None):
        return self._get(self.url_list, data=input_data)

    def patch(self, input_data=None):
        return self._patch(self.url_detail, data=input_data)


OPERATIONS = ('create', 'retrieve', 'update', 'delete', 'patch', 'list')


class MetaRestTests(type):

    def _get_rest_users(self):
        yield from (rest_user for rest_user in self._rest_users)

    def _get_tests(self):
        for rest_user in self._get_rest_users():
            for operation in OPERATIONS:
                yield 'test_{operation}_by_{rest_user.name}'.format(operation=operation, rest_user=rest_user), rest_user, operation

    def __init__(self, name, bases, attrs):
        rest_users = set()
        rest_users_names = set()

        for base in bases:
            rest_users_names |= getattr(base, '_rest_users_names', set())

        for attr, value in attrs.items():
            if value == RestUser:
                rest_users_names.add(attr)

        for rest_user_name in rest_users_names:
            rest_user = RestUser(rest_user_name, self)
            rest_users.add(rest_user)
            setattr(self, rest_user_name, rest_user)

        self._rest_users_names = rest_users_names
        self._rest_users = rest_users

    def __dir__(self):
        yield from (name for name, rest_user, operation in self._get_tests())


class RestUser(object):
    def __init__(self, name, cls):
        self.name = name
        self.cls = cls

        self.user = None
        self.allowed_operations = set()

    def __set__(self, obj, user):
        self.user = user

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return id(self.name)

    def _decorator(self, operation):
        def class_wrapper(cls):
            getattr(cls, self.name).allowed_operations.add(operation)
            return cls
        return class_wrapper

    def __getattr__(self, name):
        for operation in OPERATIONS:
            if name == 'can_{operation}'.format(operation=operation):
                return self._decorator(operation)
        raise AttributeError

    def can(self, operation):
        return operation in self.allowed_operations


class RestTests(BaseAPITestCase, metaclass=MetaRestTests):
    anonymous_user = RestUser

    def _test(self, rest_user=None, operation=''):
        if rest_user is not None:
            self.login(rest_user.user)
        input_data = getattr(
            self,
            'input_{operation}_{rest_user.name}'.format(operation=operation, rest_user=rest_user),
            getattr(self, 'input_{operation}'.format(operation=operation), None)
        )
        output_data = getattr(
            self,
            'output_{operation}_{rest_user.name}'.format(operation=operation, rest_user=rest_user),
            getattr(self, 'output_{operation}'.format(operation=operation), None)
        )
        response = getattr(self, operation)(input_data)
        if output_data is None:
            assert response.status_code == status.HTTP_204_NO_CONTENT
        else:
            assert response.status_code == status.HTTP_200_OK
            self.assert_equal(response, output_data)

    def _test_disabled(self, rest_user=None, operation=''):
        if rest_user.user is not None:
            self.login(rest_user.user)
        response = getattr(self, operation)()
        self.assert_disabled(response)

    def _get_test(self, rest_user, operation):
        if rest_user.can(operation):
            return partial(self._test, rest_user=rest_user, operation=operation)
        else:
            return partial(self._test_disabled, rest_user=rest_user, operation=operation)

    def _get_test_method(self, name):
        for test_method_name, rest_user, operation in self._get_tests():
            if name == test_method_name:
                return self._get_test(rest_user, operation)

    def __getattr__(self, attr_name):
        test_method = self._get_test_method(attr_name)
        if test_method:
            return test_method
        raise AttributeError()
