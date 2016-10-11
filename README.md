# django-rest-tests
[![PyPI version](https://badge.fury.io/py/django-rest-tests.svg)](https://badge.fury.io/py/django-rest-tests)

Semi-automated testing for API created with Django REST framework.

Django REST tests automatically checks outputs of the API according to declared inputs and users.

## basic usage

```python
from rest_tests import RestTests, RestUser

class AnonymousReadOnlyTestCase(RestTests):
    
    anonymous_user = RestUser(
        can_retrieve=True,
        can_list=True
    )
    
    url = '/tested-list/'  
    url_detail = '/tested-detail/'
    
    output_retrieve = {
        'test_attribute': 'test_data',
    }
    
    output_list = [
        ...,
        {
            'test_attribute': 'test_data',
        },
        ...
    ]
```
        
This example creates six tests: 
 * two with expected granted permissions for retrieve and list views, which check outputs against to `output_retrieve` and `output_list` structures.
 * and four "smoke tests" for create, update, delete and patch views, which expect returned 
 `HTTP_404_NOT_FOUND`, `HTTP_405_METHOD_NOT_ALLOWED` or `HTTP_403_FORBIDDEN` status.

 
## tests for more users

```python
from rest_tests import RestTests, RestUser

class MultiUserTestCase(RestTests):
    
    anonymous_user = RestUser(
        can_retrieve=True,
        can_list=True
    )
    
    logged_user = RestUser(
        user=User.objects.get(pk=1),  # some user you want to authenticate
        can_retrieve=True,
        can_list=True,
        can_create=True,
        can_update=True,
        can_delete=True,
        can_patch=True
    )
    
    url = '/tested-list/'  
    url_detail = '/tested-detail/'
    
    output_retrieve = {
        'test_attribute': 'test_data',
    }
    
    output_list = [
        ...,
        {
            'test_attribute': 'test_data',
        },
        ...
    ]
    
    input_update = {
        'test_attribute': 'test_update_data',
    }
    
    output_update = {
        'test_attribute': 'test_update_data',
    }
    
    input_patch = {
        'test_attribute': 'test_patch_data',
    }
    
    output_patch = {
        'test_attribute': 'test_patch_data',
    }
```
        
This seems pretty big, but it creates **twelve** tests in one shot. Six tests for anonymous user same as first example and six for logged user.

## Wildcards and uncertainity

You can define expected output data with some level of uncertainty via wildcard. Python offers for it Ellipsis object, which is represented by syntax construct `...`. 

### `...` in list

`...` in list means zero or more objects of any type.

```python
output_list = [
    ...,
    {'object_attribute': 'object_value'},
    ...
]
```

This means that the specific dict object is somewhere in the `ouptut_list`.


```python
output_list = [
    ...,
    {'object_attribute': 'object_value'},
]
```

This means that the specific dict object is in the end of the `ouptut_list`.

### `...` in dict

`...` used as a value with specific key means that value could be anything.

```python
output_retrieve = {
    'object_attribute': ...
}
```

Example above define, that output_retrieve must be dict object with one key 'object_atribute'. Value of the key could be anything

`...` used as a key and value means zero or more key-value pairs where key and value could be anything.

```python
output_retrieve = {
    ...: ...,
    'object_attribute': 'object_value'
}
```

This means that output_retrieve dict must have key 'object_attribute' with value 'object_value' and optionally another keys.


```python
output_retrieve = {
    ...: ...
}
```

This means that output_retrieve must be dictionary object with any keys.

### More realistic example

```python
from rest_tests import RestTests, RestUser

class MultiUserTestCase(RestTests):
    
    anonymous_user = RestUser(
        can_retrieve=True,
        can_list=True
    )
    
    output_retrieve = {
        'some_attribute': ...,
        'test_attribute': 'test_data',
    }
    
    output_list = [
        ...,
        {   
            'test_attribute': 'test_data',
        },
        ...
    ]
``` 
       
Anonymous users can only retrieve or list. Output of retrieve is a dict with two keys. One key is 'some_attribute' with any value and 'test_attribute' with specific value 'test_data'.
Output of list view must be a list contains dict object with only one key 'test_attribute' with value 'test_data'.
