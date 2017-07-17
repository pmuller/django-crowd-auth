from os.path import join, dirname, abspath

from setuptools import setup, find_packages
from pip.req import parse_requirements


def read(filename):
    with open(abspath(join(dirname(__file__), filename))) as fileobj:
        return fileobj.read()


def get_version(package):
    return [
        line for line in read('{}/__init__.py'.format(package)).splitlines()
        if line.startswith('__version__ = ')][0].split("'")[1]


NAME = 'django-crowd-auth'
PACKAGE = NAME.replace('-', '_')
VERSION = get_version(PACKAGE)


setup(
    name=NAME,
    version=VERSION,
    description='Atlassian Crowd SSO integration for Django applications',
    long_description=read('README.rst'),
    packages=find_packages(exclude=['dev']),
    author='Philippe Muller',
    author_email='philippe.muller@gmail.com',
    install_requires=[
        'django >=1.10.5',
        'crowd >=1.0.1',
    ],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
    ],
    keywords='django crowd sso authentication backend middleware',
    url='https://github.com/pmuller/django-crowd-auth',
    license='Apache License 2.0',
)
