#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sentry-Wetchat
==============

An extension for Sentry which integrates with qy-Wetchat. It will send
notifications to qy-wetchat robot.

:copyright: (c) 2019 by jerry hu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sentry-wechat",
    version='0.0.1',
    author='jerry hu',
    author_email='jerryhu_123@163.com',
    url='https://github.com/jerryhu1234/sentry-wechat',
    description='A Sentry extension which integrates with Wechat robot.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='sentry wechat',
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'sentry>=9.0.0',
        'requests',
    ],
    entry_points={
        'sentry.plugins': [
            'wechat = sentry_wechat.plugin:WechatPlugin'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        "License :: OSI Approved :: MIT License",
    ]
)
