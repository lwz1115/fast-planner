from setuptools import find_packages
from setuptools import setup

setup(
    name='multi_map_server',
    version='0.0.0',
    packages=find_packages(
        include=('multi_map_server', 'multi_map_server.*')),
)
