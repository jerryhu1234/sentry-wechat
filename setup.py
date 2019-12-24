#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sentry-Wetchat
==============

An extension for Sentry which integrates with qy-Wetchat. It will send
notifications to qy-wetchat robot.

:copyright: (c) 2019 by jerry hu, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages

# for why we need to do this.
from multiprocessing import util

with open("README.md", "r") as fh:
    long_description = fh.read()

tests_require = [
]

install_requires = [
    'sentry>=9.1.1',
]

setup(
    name='sentry-wechat',
    version='1.0.0',
    author='jerry hu',
    author_email='jerryhu_123@163.com',
    url='https://github.com/jerryhu1234/sentry-wechat',
    description='A Sentry extension which integrates with Wechat robot.',
    # long_description=__doc__,
    long_description=long_description,
    long_description_content_type="text/markdown",    
    license='BSD',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    entry_points={
        'sentry.plugins': [
            'wechat = sentry_wechat.plugin:WechatPlugin'
        ],
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
