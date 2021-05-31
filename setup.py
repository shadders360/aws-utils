#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'boto3>=1.17.84',
    'botocore>=1.20.84',
    'click>=8.0.1',
    'configparser>=5.0.2',
    'python-dateutil>=2.8.1',
    'questionary>=1.9.0',
    'rich>=10.2.2'
]

test_requirements = ['pytest>=3', ]

setup(
    author="martin shadbolt",
    author_email='grandpajava65@hotmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A few python scripts to navigate around AWS",
    entry_points={
        'console_scripts': [
            'aws_utils=aws_utils.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='aws_utils',
    name='aws_utils',
    packages=find_packages(include=['aws_utils', 'aws_utils.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/shadders360/aws_utils',
    version='0.1.0',
    zip_safe=False,
)
