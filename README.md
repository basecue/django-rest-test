# django-rest-test
[![PyPI version](https://badge.fury.io/py/django-rest-test.svg)](https://badge.fury.io/py/django-rest-test)

Semi-automated testing for API created with Django REST framework.

Django REST test automatically checks outputs of the API according to declared inputs and users.
## Installation

`$ pip install django-rest-test`

## basic usage

```python
from rest_test import RestTestCase, RestUser

class AnonymousReadOnlyTestCase(RestTestCase):
    
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
        
The example creates six tests: 
 * __two__ for retrieve and list views which check outputs against to defined `output_retrieve` and `output_list` structures.
 * and __four__ "smoke tests" for create, update, delete and patch views which expect `HTTP_404_NOT_FOUND`, `HTTP_405_METHOD_NOT_ALLOWED` or `HTTP_403_FORBIDDEN` status.

 
## tests for more users

```python
from rest_test import RestTestCase, RestUser

class MultiUserTestCase(RestTestCase):
    
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
        
This seems pretty big, but it creates **twelve** tests in one shot. Six tests for anonymous user (same as first example) and six for logged user.

## Wildcards and uncertainity

You can define expected output data with some level of uncertainty via wildcard. Python offers for it the Ellipsis object, which is represented by syntax construct `...`. 

### Ellipsis in list

`...` in list means zero or more objects of any type.

```python
output_list = [
    ...,
    {'object_attribute': 'object_value'},
    ...
]
```

This means that the specific dict object is somewhere in the `output_list`.


```python
output_list = [
    ...,
    {'object_attribute': 'object_value'},
]
```

This means that the specific dict object is in the end of the `output_list`.

### Ellipsis in dict

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

### More realistic example with ellipsis wildcards

```python
from rest_test import RestTestCase, RestUser

class MultiUserTestCase(RestTestCase):
    
    anonymous_user = RestUser(
        can_retrieve=True,
        can_list=True
    )
    
    output_retrieve = {
        'name': 'test_name',
        'description': ...,
    }
    
    output_list = [
        ...,
        {   
            'name': 'test_name',
        },
        ...
    ]
``` 
       
Anonymous users can only retrieve or list. Output of retrieve is a dict with two keys. The first key is 'name' with specific value 'test_name' and the second key is 'description' with any value.
Output of list view must be a list contains dict object with only one key 'test_attribute' with value 'test_data'.

## Typed wildcards

If you want to define the expected outputs more specific, you can use "typed" wildcards. Simple add type (int, str, dict, list) to expected output definition. Output data or subset of output will be tested only against to type. And we point out that `None` (`null` in json notation) object is not equal to any type.


```python
output_list = [
    int,
    str,
    dict
]
```

This means that the first value od `output_list` is `int`, the second is `str` and the third is `dict`.

### More realistic example with typed wildcards

```python
output_retrieve = {
    'name': 'test_name',
    'description': str,
    'some_specific_data': dict
}
```

This means that the value of key 'name' is 'test_name', key 'description' is `str` and key ''some_specific_data' is `dict`.


## Realistic example with combination of ellipsis and typed wildcards

You can combine everything together:

```python
from rest_test import RestTestCase, RestUser

class MultiUserTestCase(RestTestCase):
    
    anonymous_user = RestUser(
        can_retrieve=True,
        can_list=True
    )
    
    output_retrieve = {
        'name': 'test_name',
        'description': str,
        ...:...,
    }
    
    output_list = [
        ...,
        {   
            'name': 'test_name',
            'description': str
        },
        ...
    ]
``` 