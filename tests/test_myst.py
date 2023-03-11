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
import shutil

from pathlib import Path
from typing import NamedTuple

from md_tools.myst import (
    toctree_links,
)


# @pytest.fixture(scope="module")
# def image_file(tmp_path_factory):
#     img = compute_expensive_image()
#     fn = tmp_path_factory.mktemp("data") / "img.png"
#     img.save(fn)
#     return fn


# ----
# Test toctree_links - basic testing


class TOCTreeLinksData(NamedTuple):

    value:str
    document:Path
    root:Path
    correct_result:Path

data = []

data.append(
        TOCTreeLinksData(
            value='',
            document=Path('document.md'),
            root=Path('/docs/src'),
            correct_result=None,
    )
)

data.append(
        TOCTreeLinksData(
            value='test.md',
            document=Path('document.md'),
            root=Path('/docs/src'),
            correct_result=[Path('/docs/src/test.md')],
    )
)

data.append(
        TOCTreeLinksData(
            value='help/info/test.md',
            document=Path('start/document.md'),
            root=Path('/docs/src'),
            correct_result=[Path('/docs/src/start/help/info/test.md')],
    )
)

data.append(
        TOCTreeLinksData(
            value='../test.md',
            document=Path('start/document.md'),
            root=Path('/docs/src'),
            correct_result=[Path('/docs/src/test.md')],
    )
)

data.append(
        TOCTreeLinksData(
            value='./test.md',
            document=Path('start/document.md'),
            root=Path('/docs/src'),
            correct_result=[Path('/docs/src/start/test.md')],
    )
)


@pytest.mark.parametrize("data", data)
def test_toctree_links(data):

    result = toctree_links(data.value, data.document, data.root)

    assert data.correct_result == result


# ----
# Test toctree_links - glob testing

# *
# index*
# test/*



@pytest.fixture(scope="module")
def docs_src_folder(tmp_path_factory):

    #/docs
    #   /src
    #       /docs_0.md
    #       /docs_1.md
    #       /docs_2.md
    #       /docs_3.md
    #       /docs_4.md
    #       /docs_5.md
    #       /docs_6.md
    #   /help
    #       /help_0.md
    #       /help_1.md
    #       /help_2.md
    #       /help_3.md

    # Create a temporary directory for the test
    docs = tmp_path_factory.mktemp('testing') / Path('docs')
    docs.mkdir(parents=True, exist_ok=True)

    src = docs / 'src'
    src.mkdir(parents=True, exist_ok=True)

    for i in range(6):
        file = src / Path(f'doc_{i}.md')
        file.touch()

    help_path = docs / 'help'
    help_path.mkdir(parents=True, exist_ok=True)

    for i in range(4):
        file = help_path / Path(f'help_{i}.md')
        file.touch()

    for i in range(4):
        file = help_path / Path(f'P_PPP_help_{i}.md')
        file.touch()


    # Yield the test folder to the tests
    yield docs

    # Clean up the test folder after the tests are done
    shutil.rmtree(docs)


data = []


data.append(
        TOCTreeLinksData(
            value='*',
            document=Path('src/doc_3.md'),
            root=None,
            correct_result=[
                Path('src/doc_0.md'),
                Path('src/doc_1.md'),
                Path('src/doc_2.md'),
                Path('src/doc_4.md'),
                Path('src/doc_5.md'),
            ],
    )
)


data.append(
        TOCTreeLinksData(
            value='*',
            document=Path('help/help_2.md'),
            root=None,
            correct_result=[
                Path('help/help_0.md'),
                Path('help/help_1.md'),
                Path('help/help_3.md'),
                Path('help/P_PPP_help_0.md'),
                Path('help/P_PPP_help_1.md'),
                Path('help/P_PPP_help_2.md'),
                Path('help/P_PPP_help_3.md'),
            ],
    )
)


data.append(
        TOCTreeLinksData(
            value='help*.md',
            document=Path('help/help_2.md'),
            root=None,
            correct_result=[
                Path('help/help_0.md'),
                Path('help/help_1.md'),
                Path('help/help_3.md'),
            ],
    )
)

data.append(
        TOCTreeLinksData(
            value='*help*.md',
            document=Path('help/help_2.md'),
            root=None,
            correct_result=[
                Path('help/help_0.md'),
                Path('help/help_1.md'),
                Path('help/help_3.md'),
                Path('help/P_PPP_help_0.md'),
                Path('help/P_PPP_help_1.md'),
                Path('help/P_PPP_help_2.md'),
                Path('help/P_PPP_help_3.md'),
            ],
    )
)


data.append(
        TOCTreeLinksData(
            value='/help/*',
            document=Path('help/help_2.md'),
            root=None,
            correct_result=[
                Path('help/help_0.md'),
                Path('help/help_1.md'),
                Path('help/help_3.md'),
                Path('help/P_PPP_help_0.md'),
                Path('help/P_PPP_help_1.md'),
                Path('help/P_PPP_help_2.md'),
                Path('help/P_PPP_help_3.md'),
            ],
    )
)


@pytest.mark.parametrize("data", data)
def test_toctree_links(data, docs_src_folder):

    value = data.value
    root = docs_src_folder
    document = root / data.document

    correct_result=[root/ p for p in data.correct_result]

    result = toctree_links(value, document, root)

    assert sorted(correct_result) == sorted(result)
