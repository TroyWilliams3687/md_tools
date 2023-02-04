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
    MarkdownImageLinkRuleResult,
)

from md_tools.markdown import (
    LinkLineNumber,
    markdown_links,
    markdown_image_links,
    markdown_all_links,
)


# ----
# Test markdown_links

# this is an integration test because this method makes use of outside_fence


data = []

data.append(
    (
        ("3 Test 1 - basic line [here](https://www.bluebill.net)",),
        [
            LinkLineNumber(
                0,
                "3 Test 1 - basic line [here](https://www.bluebill.net)",
                [
                    MarkdownLinkRuleResult(
                        full="[here](https://www.bluebill.net)",
                        text="here",
                        url="https://www.bluebill.net",
                    )
                ],
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
                [
                    MarkdownLinkRuleResult(
                        full="[here](https://www.bluebill.net)",
                        text="here",
                        url="https://www.bluebill.net",
                    )
                ],
            ),
            LinkLineNumber(
                9,
                "5 Test 1 - [basic](./test.md) line",
                [
                    MarkdownLinkRuleResult(
                        full="[basic](./test.md)",
                        text="basic",
                        url="./test.md",
                    )
                ],
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


# ----
# Testing markdown_image_links


data = []

data.append(
    (
        ("0. The image in question: ![here](https://www.bluebill.net/image1.png)",),
        [
            LinkLineNumber(
                0,
                "0. The image in question: ![here](https://www.bluebill.net/image1.png)",
                [
                    MarkdownImageLinkRuleResult(
                        full="![here](https://www.bluebill.net/image1.png)",
                        text="here",
                        url="https://www.bluebill.net/image1.png",
                    )
                ],
            ),
        ],
    )
)

data.append(
    (
        (
            "0. The image in question: ![here](https://www.bluebill.net/image1.png)",
            "1. ![test](../image1.png)",
            "2. Nothing to See here...",
            "3. Here be Dragons",
            "3. Here be Dragons",
            "3. Here be Dragons",
            "1. ![image 1](../image1.png) and ![image 2](./image2.png)",
        ),

        [
            LinkLineNumber(
                0,
                "0. The image in question: ![here](https://www.bluebill.net/image1.png)",
                [
                    MarkdownImageLinkRuleResult(
                        full="![here](https://www.bluebill.net/image1.png)",
                        text="here",
                        url="https://www.bluebill.net/image1.png",
                    )
                ],
            ),
            LinkLineNumber(
                1,
                "1. ![test](../image1.png)",
                [
                    MarkdownImageLinkRuleResult(
                        full="![test](../image1.png)",
                        text="test",
                        url="../image1.png",
                    )
                ],
            ),
            LinkLineNumber(
                6,
                "1. ![image 1](../image1.png) and ![image 2](./image2.png)",
                [
                    MarkdownImageLinkRuleResult(
                        full="![image 1](../image1.png)",
                        text="image 1",
                        url="../image1.png",
                    ),
                    MarkdownImageLinkRuleResult(
                        full="![image 2](./image2.png)",
                        text="image 2",
                        url="./image2.png",
                    ),
                ],
            ),
        ],
    )
)


@pytest.mark.integration_test
@pytest.mark.parametrize("data", data)
def test_markdown_image_links(data):

    lines, reference = data

    for left, right in zip(reference, markdown_image_links(lines)):
        assert left == right

# ----
# Testing markdown_all_links


data = []

data.append(
    (
        (
            "0. Image: ![here](https://www.bluebill.net/image1.png)",
            "1. link: [test](../image1.md)",
        ),

        [
            LinkLineNumber(
                0,
                "0. Image: ![here](https://www.bluebill.net/image1.png)",
                [
                    MarkdownImageLinkRuleResult(
                        full="![here](https://www.bluebill.net/image1.png)",
                        text="here",
                        url="https://www.bluebill.net/image1.png",
                    )
                ],
            ),
            LinkLineNumber(
                1,
                "1. link: [test](../image1.md)",
                [
                    MarkdownLinkRuleResult(
                        full="[test](../image1.md)",
                        text="test",
                        url="../image1.md",
                    )
                ],
            ),
        ],
    )
)

data.append(
    (
        (
            "0. Image: ![here](https://www.bluebill.net/image1.png) and link: [link 1](../test/file.txt)",
            "1. link: [test](../image1.md) and ![image](https://test.com/image.png)",
        ),

        [
            LinkLineNumber(
                0,
                "0. Image: ![here](https://www.bluebill.net/image1.png) and link: [link 1](../test/file.txt)",
                [
                    MarkdownLinkRuleResult(
                        full="[link 1](../test/file.txt)",
                        text="link 1",
                        url="../test/file.txt",
                    ),
                    MarkdownImageLinkRuleResult(
                        full="![here](https://www.bluebill.net/image1.png)",
                        text="here",
                        url="https://www.bluebill.net/image1.png",
                    ),
                ],
            ),
            LinkLineNumber(
                1,
                "1. link: [test](../image1.md) and ![image](https://test.com/image.png)",
                [
                    MarkdownLinkRuleResult(
                        full="[test](../image1.md)",
                        text="test",
                        url="../image1.md",
                    ),
                    MarkdownImageLinkRuleResult(
                        full="![image](https://test.com/image.png)",
                        text="image",
                        url="https://test.com/image.png",
                    ),
                ],
            ),
        ],
    )
)

# NOTE: The order of the result list matters in the testing.

@pytest.mark.integration_test
@pytest.mark.parametrize("data", data)
def test_markdown_all_links(data):

    lines, reference = data

    for left, right in zip(reference, markdown_all_links(lines)):
        assert left == right


