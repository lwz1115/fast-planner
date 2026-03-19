#!/usr/bin/env python3
"""
Setup script for fastapi_planner package.
"""

from setuptools import setup

setup(
    name='fastapi_planner',
    version='0.1.0',
    description='FastAPI REST interface for Fast-Planner ROS2 trajectory planning',
    author='Fast-Planner Team',
    packages=['fastapi_planner'],
    package_dir={'fastapi_planner': '.'},
    install_requires=[
        'fastapi>=0.68.0',
        'uvicorn[standard]>=0.15.0',
        'pydantic>=1.8.0',
        'numpy>=1.19.0',
        'opencv-python>=4.5.0',
        'PyYAML>=5.4.0',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'fastapi-planner=fastapi_planner.main:main',
        ],
    },
)

