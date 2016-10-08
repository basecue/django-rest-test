# django-rest-tests
[![PyPI version](https://badge.fury.io/py/django-rest-tests.svg)](https://badge.fury.io/py/django-rest-tests)

Semi-automated testing for API created with Django REST framework.

Django REST tests automatically checks outputs of the API according to declared inputs and users.

## basic usage

.. code-block:: python

    from rest_tests import RestTests, RestUser

    class AnnonymousReadOnlyTestCase(RestTests):
        
        annonymous_user = RestUser(
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
        
This example creates six tests: 
 * two with expected granted permissions for retrieve and list views, which check outputs against to `output_retrieve` and `output_list` structures.
 * and four "smoke tests" for create, update, delete and patch views, which expect returned 
 `HTTP_404_NOT_FOUND`, `HTTP_405_METHOD_NOT_ALLOWED` or `HTTP_403_FORBIDDEN` status.
 
## tests for more users

.. code-block:: python

    from rest_tests import RestTests, RestUser

    class MultiUserTestCase(RestTests):
        
        annonymous_user = RestUser(
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
        
This seems pretty big, but it creates **twelve** tests in one shot. Six tests for annonymous user same as first example and six for logged user.

## wildcards and uncertainity

_"Explicit is better than implicit."_

.. code-block:: python

    from rest_tests import RestTests, RestUser

    class MultiUserTestCase(RestTests):
        
        annonymous_user = RestUser(
            can_retrieve=True,
            can_list=True
        )
        
        logged_user = RestUser(
            user=User.objects.get(pk=1),  # some user you want to authenticate
            can_retrieve=True,
            can_list=True,
            can_create=True,
            can_update=...,
            can_delete=...,
            can_patch=...
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
        
