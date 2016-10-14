from functools import partial

from rest_framework import status
from rest_framework.test import APITestCase
from pprint import pformat
from collections import OrderedDict

from rest_framework.utils.serializer_helpers import ReturnList


def compare_lists(data, expected_data):
    data_gen = (item for item in data)
    expected_data_gen = (item for item in expected_data)

    for value in expected_data_gen:
        if value is ...:
            try:
                next_value = expected_data_gen.send(None)
            except StopIteration:
                # last item is ellipsis
                return True

            if next_value is ...:
                raise TypeError('Consecutively usage of ... (Ellipsis) is not allowed in list.')

            try:
                while not compare(data_gen.send(None), next_value):
                    pass
            except StopIteration:
                # next expected item is not in data
                return False

        else:
            try:
                data_item = data_gen.send(None)
            except StopIteration:
                # there are more expected items
                return False

            if not compare(data_item, value):
                # expected item is not in data
                return False

    try:
        data_gen.send(None)
    except StopIteration:
        return True
    else:
        # More items in data
        return False


def compare_dicts(data, expected_data):
    subset = False

    # subset
    if ... in expected_data:
        if expected_data[...] is ...:
            subset = True
        else:
            raise TypeError('Bad usage of ... (Ellipsis).')

    compared_keys = []

    for key, value in expected_data.items():
        if key is ...:
            continue

        if value is ...:
            if key not in data:
                # Key is not found in data
                return False

            else:
                compared_keys.append(key)
        else:
            if key in data:
                if compare(data[key], expected_data[key]):
                    compared_keys.append(key)
                else:
                    # values are not the same
                    return False

            else:
                # Key is not found in data
                return False

    if not subset:
        if len(compared_keys) != len(data):
            # More items in data
            return False

    return True


def compare(data, expected_data):

    # if expected_data is type, only test if type of data is the same
    if isinstance(expected_data, type) and type(data) == expected_data:
        return True

    expected_data_type = type(expected_data)

    if expected_data_type != type(data):
        # different types
        return False

    if expected_data_type == list:
        return compare_lists(data, expected_data)
    elif expected_data_type == dict:
        return compare_dicts(data, expected_data)
    else:
        return data == expected_data


def convert_data(data):
    if type(data) == list or isinstance(data, ReturnList):
        return [convert_data(item) for item in data]
    elif type(data) == dict or isinstance(data, OrderedDict):
        return {key: convert_data(value) for key, value in data.items()}
    else:
        return data


class BaseAPITestCase(APITestCase):
    def _request(self, method, url, data=None):
        response = getattr(self.client, method)(url, data=data, format='json')
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
    def assert_disabled(self, status_code):
        msg = pformat(
            dict(
                response_status_code=status_code,
                expected_status_codes=(
                    status.HTTP_404_NOT_FOUND,
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                    status.HTTP_403_FORBIDDEN
                )
            )
        )
        assert status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_403_FORBIDDEN
        ), msg

    def assert_compare(self, data, expected_data):
        data = convert_data(data)
        msg = pformat(
            dict(
                response_data=data,
                expected_data=expected_data
            )
        )
        assert compare(data, expected_data), msg

    url = ''
    url_detail = ''

    def create(self, input_data=None):
        return self._post(self.url, data=input_data)

    def retrieve(self, input_data=None):
        return self._get(self.url_detail, data=input_data)

    def update(self, input_data=None):
        return self._put(self.url_detail, data=input_data)

    def delete(self, input_data=None):
        return self._delete(self.url_detail, data=input_data)

    def list(self, input_data=None):
        return self._get(self.url, data=input_data)

    def patch(self, input_data=None):
        return self._patch(self.url_detail, data=input_data)

    def _login(self, user):
        self.client.force_authenticate(user=user)


OPERATIONS = ('create', 'retrieve', 'update', 'delete', 'patch', 'list')


class AllRestUsers():
    def _decorator(self, operation):
        def class_wrapper(cls):
            for rest_user in cls.rest_users:
                rest_user.allowed_operations.add(operation)
            return cls
        return class_wrapper

    def __getattr__(self, name):
        for operation in OPERATIONS:
            if name == 'can_{operation}'.format(operation=operation):
                return self._decorator(operation)
        raise AttributeError


class MetaRestTestCase(type):

    @property
    def rest_users(self):
        yield from (rest_user for rest_user in self._rest_users)

    @property
    def test_names(self):
        for rest_user in self.rest_users:
            for operation in OPERATIONS:
                yield 'test_{operation}_by_{rest_user.name}'.format(
                    operation=operation, rest_user=rest_user
                ), rest_user, operation

    def __getattr__(self, attr_name):
        for test_name, rest_user, operation in self.test_names:
            if test_name == attr_name:
                return lambda s: True
        raise AttributeError()

    def __init__(cls, name, bases, attrs):
        rest_users = set()
        rest_users_names = set()

        for base in bases:
            rest_users_names |= getattr(base, '_rest_users_names', set())

        for attr, value in attrs.items():
            if isinstance(value, type) and issubclass(value, RestUser):
                rest_users_names.add(attr)
            elif isinstance(value, RestUser):
                if value.name is None:
                    value.name = attr
                rest_users.add(value)

        for rest_user_name in rest_users_names:
            rest_user = RestUser(name=rest_user_name)
            rest_users.add(rest_user)
            setattr(cls, rest_user_name, rest_user)

        cls._rest_users_names = rest_users_names
        cls._rest_users = rest_users
        super().__init__(name, bases, attrs)

    def __dir__(self):
        return [test_name for test_name, rest_user, operation in self.test_names] + super().__dir__()


class RestUser(object):
    def __init__(self, name=None, user=None, **kwargs):
        self.name = name
        self.user = user
        self.allowed_operations = set()

        for operation in OPERATIONS:
            kwarg = 'can_{}'.format(operation)
            if kwargs.get(kwarg, False):
                self.allowed_operations.add(operation)

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


class RestTestCase(BaseAPITestCase, metaclass=MetaRestTestCase):

    all_users = AllRestUsers()
    anonymous_user = RestUser
    output_status_create = status.HTTP_201_CREATED

    def _get_input_data(self, rest_user, operation):
        return getattr(
            self,
            'input_{operation}_{rest_user.name}'.format(operation=operation, rest_user=rest_user),
            getattr(self, 'input_{operation}'.format(operation=operation), None)
        )

    def _get_output_data(self, rest_user, operation):
        return getattr(
            self,
            'output_{operation}_{rest_user.name}'.format(operation=operation, rest_user=rest_user),
            getattr(self, 'output_{operation}'.format(operation=operation), None)
        )

    def _get_output_status(self, rest_user, operation):
        return getattr(
            self,
            'output_status_{operation}_{rest_user.name}'.format(operation=operation, rest_user=rest_user),
            getattr(self, 'output_status_{operation}'.format(operation=operation), status.HTTP_200_OK)
        )

    def _test(self, rest_user=None, operation=''):
        print("Operation '{operation}' for '{rest_user.name}' is enabled.".format(
            operation=operation, rest_user=rest_user)
        )
        if rest_user is not None:
            self._login(rest_user.user)

        input_data = self._get_input_data(rest_user, operation)

        output_data = self._get_output_data(rest_user, operation)

        output_status = self._get_output_status(rest_user, operation)

        response = getattr(self, operation)(input_data)

        if output_data is None:
            assert response.status_code == status.HTTP_204_NO_CONTENT
        else:
            assert output_status == output_status
            # TODO - maybe: if hasattr(response, 'data') else None
            self.assert_compare(response.data, output_data)

    def _get_test(self, rest_user, operation):
        if rest_user.can(operation):
            return partial(self._test, rest_user=rest_user, operation=operation)
        else:
            return partial(self._test_disabled, rest_user=rest_user, operation=operation)

    def _test_disabled(self, rest_user=None, operation=''):
        print("Operation '{operation}' for '{rest_user.name}' is disabled.".format(operation=operation, rest_user=rest_user))
        if rest_user.user is not None:
            self.login(rest_user.user)

        # no input data
        input_data_list = [None]

        # input data for allowed users
        for another_rest_user in self.__class__.rest_users:
            if rest_user != another_rest_user and another_rest_user.can(operation):
                another_input_data = self._get_input_data(another_rest_user, operation)
                if another_input_data not in input_data_list:
                    input_data_list.append(another_input_data)

        for input_data in input_data_list:
            response = getattr(self, operation)(input_data)
            self.assert_disabled(response.status_code)

    def __getattr__(self, attr_name):
        for test_name, rest_user, operation in self.__class__.test_names:
            if test_name == attr_name:
                return self._get_test(rest_user, operation)
        raise AttributeError()
