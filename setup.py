from setuptools import setup, find_packages

setup(
    name='django-rest-tests',
    version='0.1.0a',
    url='http://github.com/baseclue/django-rest-tests',
    license='Apache 2.0',
    author='Jan Češpivo',
    author_email='jan.cespivo@gmail.com',
    description='Semi-automated testing for Django REST framework API',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=["django", "djangorestframework"],
    test_requires=["pytest", "pytest-django"]
)
