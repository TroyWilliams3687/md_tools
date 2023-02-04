#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2020 Troy Williams

uuid       = 7ee08c52-a4ba-11ed-98e8-bd915a7135be
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2023-02-04
-----------

Integration testing

"""

import pytest

from md_tools.markdown_classifiers import (
    MarkdownLinkRuleResult,
)

from md_tools.markdown import (
    LinkLineNumber,
    markdown_links,
)



# ----
# Test markdown_links

# this is an integration test because this method makes use of outside_fence


data = []

data.append(
    (
        (
            "3 Test 1 - basic line [here](https://www.bluebill.net)",
        ),
        [
            LinkLineNumber(
                0,
                "3 Test 1 - basic line [here](https://www.bluebill.net)",
                [MarkdownLinkRuleResult(
                    full="[here](https://www.bluebill.net)",
                    text="here",
                    url="https://www.bluebill.net",
                )],
            ),
        ],
    )
)


data.append(
    (
        (
            "1 Test 1 - basic line http://www.random.xyz",
            "2 Test 1 - basic line",
            "``` python",
            "import re",
            "print('test')",
            "# [link](http://www.python.org)",
            "```",
            "3 Test 1 - basic line [here](https://www.bluebill.net)",
            "4 Test 1 - basic line",
            "5 Test 1 - [basic](./test.md) line",
        ),
        [
            LinkLineNumber(
                7,
                "3 Test 1 - basic line [here](https://www.bluebill.net)",
                [MarkdownLinkRuleResult(
                    full="[here](https://www.bluebill.net)",
                    text="here",
                    url="https://www.bluebill.net",
                )],
            ),
            LinkLineNumber(
                9,
                "5 Test 1 - [basic](./test.md) line",
                [MarkdownLinkRuleResult(
                        full="[basic](./test.md)",
                        text="basic",
                        url="./test.md",
                    )],
            ),
        ],
    )
)

@pytest.mark.integration_test
@pytest.mark.parametrize("data", data)
def test_markdown_links(data):

    lines, reference = data

    for left, right in zip(reference, markdown_links(lines)):
        assert left == right


