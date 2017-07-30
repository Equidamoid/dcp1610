#!/usr/bin/env python3

from distutils.core import setup

setup(
    name="dcp1610",
    version='0.1',
    description="Brother network scanner protocol implementation",
    author='Vladimir Shapranov',
    author_email='equidamoid@gmail.com',
    url='https://github.com/Equidamoid/dcp1610',
    packages=['dcp1610'],
    scripts=['dcp1610-scan'],
    requires=['easysnmp', 'zeroconf', 'Pillow']
)

