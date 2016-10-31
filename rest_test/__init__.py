from functools import partial

from rest_framework import status
from rest_framework.test import APITestCase
from pprint import pformat
from collections import OrderedDict, namedtuple

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



OperationDefinition = namedtuple('OperationDefinition', ['method', 'url'])
OPERATIONS = {
    'create': OperationDefinition(method='post', url='url'),
    'retrieve': OperationDefinition(method='get', url='url_detail'),
    'update': OperationDefinition(method='put', url='url_detail'),
    'delete': OperationDefinition(method='delete', url='url_detail'),
    'patch': OperationDefinition(method='patch', url='url_detail'),
    'list': OperationDefinition(method='get', url='url')
}


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
        if not self.__test__:
            raise StopIteration()

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

        # pytest compatible support for excluding whole TestCase - ie. for inheritance and for some test suits
        if '__test__' not in attrs:
            cls.__test__ = attrs.get('_{}__test'.format(name), True)

        cls._rest_users_names = rest_users_names
        cls._rest_users = rest_users
        super().__init__(name, bases, attrs)

    def __dir__(self):
        return [test_name for test_name, rest_user, operation in self.test_names] + super().__dir__()


class RestUser(object):
    def __init__(self, name=None, user=None, **kwargs):
        self.name = name
        self.bound_user = user
        self.allowed_operations = set()

        for operation in OPERATIONS:
            kwarg = 'can_{}'.format(operation)
            if kwargs.get(kwarg, False):
                self.allowed_operations.add(operation)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return id(self.name)

    def bind_user(self, user):
        self.bound_user = user

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


class RestTestCase(APITestCase, metaclass=MetaRestTestCase):

    all_users = AllRestUsers()
    anonymous_user = RestUser
    output_status_create = status.HTTP_201_CREATED

    __test = False

    def assert_disabled(self, status_code):
        expected_status_codes = (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_403_FORBIDDEN
        )

        msg =pformat(dict(
            response_status_code=status_code,
            expected_status_codes=expected_status_codes
        ))

        assert status_code in expected_status_codes, msg

    def assert_compare(self, data, expected_data):
        data = convert_data(data)

        msg = pformat(dict(
            response_data=data,
            expected_data=expected_data
        ))
        assert compare(data, expected_data), msg

    def assert_status_code(self, response_status_code, expected_status_code):
        msg = "Expected response status code is '{expected_status_code}' but got '{response_status_code}'.".format(
            response_status_code=response_status_code,
            expected_status_code=expected_status_code
        )
        assert response_status_code == expected_status_code, msg

    def login(self, user):
        self.client.force_authenticate(user=user)

    def _request(self, method, url, data):
        response = getattr(self.client, method)(url, data=data, format='json')
        return response

    url = ''
    url_detail = ''

    def _get_method_url_for_operation(self, operation):
        operation_definition = OPERATIONS[operation]
        return operation_definition.method, getattr(self, operation_definition.url)

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

    def _get_output_status(self, rest_user, operation, default_output_status):
        return getattr(
            self,
            'output_status_{operation}_{rest_user.name}'.format(operation=operation, rest_user=rest_user),
            getattr(self, 'output_status_{operation}'.format(operation=operation), default_output_status)
        )

    def _wrap_test(self, test, message, operation, rest_user):
        def wrapper():
            method, url = self._get_method_url_for_operation(operation)

            if rest_user is not None:
                self.login(rest_user.bound_user)

            get_response = partial(self._request, method, url)

            try:
                test(operation, rest_user, get_response)
            except AssertionError as assertion:
                assertion_message = "{message}\nRequest method: '{method}' URL: {url}\n{assertion_message}".format(
                    message=message,
                    method=method,
                    url=url,
                    assertion_message=assertion.args[0]
                )
                assertion.args = [assertion_message]
                raise
        return wrapper

    def _test(self, operation, rest_user, get_response):

        input_data = self._get_input_data(rest_user, operation)

        expected_output_data = self._get_output_data(rest_user, operation)

        if expected_output_data is None:
            default_expected_output_status = status.HTTP_204_NO_CONTENT
        else:
            default_expected_output_status = status.HTTP_200_OK

        expected_status_code = self._get_output_status(rest_user, operation, default_expected_output_status)

        if expected_output_data is None:
            msg = "Define output data to value other than 'None' or change expected status code to HTTP_204_NO_CONTENT ({status_code})".format(

                status_code=status.HTTP_204_NO_CONTENT
            )
            assert expected_status_code == status.HTTP_204_NO_CONTENT, msg

        response = get_response(input_data)

        response_status_code = response.status_code
        response_data = getattr(response, 'data', None)

        self.assert_status_code(response_status_code, expected_status_code)
        self.assert_compare(response_data, expected_output_data)

    def _get_test(self, rest_user, operation):
        if rest_user.can(operation):
            message = "Operation '{operation}' for '{rest_user.name}' is enabled.".format(
                operation=operation, rest_user=rest_user
            )
            return self._wrap_test(self._test, message, rest_user=rest_user, operation=operation)
        else:
            message = "Operation '{operation}' for '{rest_user.name}' is disabled.".format(
                operation=operation, rest_user=rest_user
            )
            return self._wrap_test(self._test_disabled, message, rest_user=rest_user, operation=operation)

    def _test_disabled(self, operation, rest_user, get_response):
        # no input data
        input_data_list = [None]

        # input data for allowed users
        for another_rest_user in self.__class__.rest_users:
            if rest_user != another_rest_user and another_rest_user.can(operation):
                another_input_data = self._get_input_data(another_rest_user, operation)
                if another_input_data not in input_data_list:
                    input_data_list.append(another_input_data)

        for input_data in input_data_list:
            response = get_response(input_data)
            self.assert_disabled(response.status_code)

    def __getattr__(self, attr_name):
        for test_name, rest_user, operation in self.__class__.test_names:
            if test_name == attr_name:
                return self._get_test(rest_user, operation)
        raise AttributeError()
