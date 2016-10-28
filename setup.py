from setuptools import setup

setup(
    name='django-rest-test',
    version='0.7.3b',
    url='http://github.com/baseclue/django-rest-test',
    license='Apache 2.0',
    author='Jan Češpivo',
    author_email='jan.cespivo@gmail.com',
    description='Semi-automated testing for Django REST framework API',
    packages=['rest_test'],
    install_requires=["djangorestframework"],
    test_requires=["pytest", "pytest-django"]
)
