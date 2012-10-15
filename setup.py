# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sphero',
    version='0.0.0',
    description='A python client for Sphero.',
    long_description=readme,
    author='Chris Faulkner',
    author_email='thefaulkner@gmail.com',
    url='http://github.com/faulkner/sphero',
    license=license,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyserial==2.6',
    ],
    tests_require=['nose'],
    test_suite='nose.collector',
)
