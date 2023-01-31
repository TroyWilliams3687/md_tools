#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Troy Williams

# uuid   =
# author = Troy Williams
# email  = troy.williams@bluebill.net
# date   =
# -----------

"""
This is a template python script for use in creating other classes and applying
a standard to them
"""

# ------------
# System Modules - Included with Python

import re

# ------------
# 3rd Party - From PyPI

# ------------
# Custom Modules

# -------------

def url_path_to_dict(path):
    pattern = (r'^'
               r'((?P<schema>.+?)://)?'
               r'((?P<user>.+?)(:(?P<password>.*?))?@)?'
               r'(?P<host>.*?)'
               r'(:(?P<port>\d+?))?'
               r'(?P<path>/.*?)?'
               r'(?P<query>[?].*?)?'
               r'$'
               )
    regex = re.compile(pattern)
    m = regex.match(path)
    d = m.groupdict() if m is not None else None

    return d

def main():
    print( url_path_to_dict('http://example.example.com/example/example/example.html'))
    print( url_path_to_dict('ftp://example.example.com/example/example/example.html'))
    print( url_path_to_dict('://example.example.com/example/example/example.html'))
    print( url_path_to_dict('./example/example/example.html'))
    print( url_path_to_dict('./example/example/example.html#section1'))



if __name__ == '__main__':
    main()
