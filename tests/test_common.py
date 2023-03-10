#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2020 Troy Williams

uuid       = 2fc2598a-341d-11eb-bf3c-ab85e03a1801
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2020-12-01
-----------


"""

import pytest

from pathlib import Path
from typing import NamedTuple

from md_tools.common import (
    str_to_file,
)


# @pytest.fixture(scope="module")
# def image_file(tmp_path_factory):
#     img = compute_expensive_image()
#     fn = tmp_path_factory.mktemp("data") / "img.png"
#     img.save(fn)
#     return fn


# ----
# Test str_to_file

# data = []

# data.append(("https://github.com/tomduck/pandoc-fignos", True))
# data.append(("http://github.com/tomduck/pandoc-fignos", True))
# data.append(("ftp://github.com/tomduck/pandoc-fignos", True))

# data.append(("http://github.com/ tomduck/ pandoc-fignos", False))
# data.append(("ftp:// github.com/ tomduck/ pandoc-fignos", False))
# data.append(("ftps://github.com/tomduck/pandoc-fignos", False))
# data.append(("www.google.ca", False))
# data.append(("google.com", False))


class StrToFileData(NamedTuple):

    value:str
    document:Path
    root:Path
    correct_result:Path

data = []

data.append(
        StrToFileData(
            value='test.md',
            document=Path('document.md'),
            root=Path('/'),
            correct_result=Path('test.md'),
    )
)

data.append(
        StrToFileData(
            value='docs/test.md',
            document=Path('document.md'),
            root=Path('/'),
            correct_result=Path('docs/test.md'),
    )
)




@pytest.mark.parametrize("data", data)
def test_str_to_file(data):

    result = str_to_file(data.value, data.document, data.root)

    assert data.correct_result == result
