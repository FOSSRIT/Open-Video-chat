#!/usr/bin/env python2.7

# Imports
import os
from setuptools import setup, find_packages

# Paths
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(os.path.dirname(__file__) + '../', 'README.md')).read()

# Setup Parameters
setup(
    name='OpenVideoChat',
    version='2.0',
    description='A video chat client that uses GStreamer and Jabber servers to enable video communication.',
    long_description=README,
    license="GPLv3+",
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Casey DeLorme, Caleb Coffie, Luke Macken, Remy DeCausemaker, Fran Rogers, Taylor Rose, Justin Lewis',
    author_email='cxd4280@rit.edu, CalebCoffie@gmail.com, lmacken@redhat.com, remyd@civx.us, fran@dumetella.net, tjr1351@rit.edu, jlew.blackout@gmail.com',
    url='https://github.com/FOSSRIT/Open-Video-chat',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
