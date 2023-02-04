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
    markdown_all_relative_links,
    MarkdownDocument,
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


# ----
# Test markdown_all_relative_links

data = []

data.append(
    (
        (
            "0. Image: ![here](https://www.bluebill.net/image1.png)",
            "1. link: [test](../image1.md)",
        ),
        [
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
            "0. Image: ![here](https://www.bluebill.net/image1.png) The relative link: [test](../image1.md)",
        ),
        [
            LinkLineNumber(
                0,
                "0. Image: ![here](https://www.bluebill.net/image1.png) The relative link: [test](../image1.md)",
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


# NOTE: The order of the result list matters in the testing.


@pytest.mark.integration_test
@pytest.mark.parametrize("data", data)
def test_markdown_all_relative_links(data):

    lines, reference = data

    for left, right in zip(reference, markdown_all_relative_links(lines)):
        assert left == right


# ----
# Test MarkdownDocument

test_content = (
    "# Test Data - Links, Images and other Items",
    "Here is an image: ![relative image](../image1.png) and ![absolute](https://www.find.com/image.png)",
    "Some python code that we'll ignore:",
    "``` python",
    "import re",
    "print('test')",
    "# [link](http://www.python.org)",
    "```",
    "3 Test 1 - basic line [here](https://www.bluebill.net)",
    "4 Test 1 - basic line",
    "5 Test 1 - [basic](./test.md) line",
    "```",
    "import re",
    "```",
    "print('test')",
    "# [web](http://www.python.org) and [local](../md.txt)",
    "```",
)


# https://docs.pytest.org/en/7.1.x/how-to/tmp_path.html
@pytest.fixture(scope="session")
def create_markdown_file(tmp_path_factory):

    fn = tmp_path_factory.mktemp("data") / "test.md"
    fn.write_text("\n".join(test_content))

    return fn


data = []

data.append(
    (
        "Here is an image: ![relative image](../image1.png) and ![absolute](https://www.find.com/image.png)",
        [1],
    )
)
data.append(("import re", [4, 12]))
data.append(("import redtime", None))


@pytest.mark.parametrize("data", data)
def test_MarkdownDocument_line_lookup(create_markdown_file, data):

    line, numbers = data

    md = MarkdownDocument(create_markdown_file)

    # assert md.filename.name == "test.md"

    assert md.line_lookup(line) == numbers


data = []

data.append(
    [
        LinkLineNumber(
            8,
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
            10,
            "5 Test 1 - [basic](./test.md) line",
            [
                MarkdownLinkRuleResult(
                    full="[basic](./test.md)",
                    text="basic",
                    url="./test.md",
                )
            ],
        ),
        LinkLineNumber(
            15,
            "# [web](http://www.python.org) and [local](../md.txt)",
            [
                MarkdownLinkRuleResult(
                    full="[web](http://www.python.org)",
                    text="web",
                    url="http://www.python.org",
                ),
                MarkdownLinkRuleResult(
                    full="[local](../md.txt)",
                    text="local",
                    url="../md.txt",
                ),
            ],
        ),
    ]
)


@pytest.mark.parametrize("data", data)
def test_MarkdownDocument_links(create_markdown_file, data):

    links = data

    md = MarkdownDocument(create_markdown_file)

    assert md.links == links


# test_content = (
#     "# Test Data - Links, Images and other Items",
#     "Here is an image: ![relative image](../image1.png) and ![absolute](https://www.find.com/image.png)",
#     "Some python code that we'll ignore:",
#     "``` python",
#     "import re",
#     "print('test')",
#     "# [link](http://www.python.org)",
#     "```",
#     "3 Test 1 - basic line [here](https://www.bluebill.net)",
#     "4 Test 1 - basic line",
#     "5 Test 1 - [basic](./test.md) line",
#     "```",
#     "import re",
#     "```",
#     "print('test')",
#     "# [web](http://www.python.org) and [local](../md.txt)",
#     "```",
# )


data = []

data.append(
    [
        LinkLineNumber(
            1,
            "Here is an image: ![relative image](../image1.png) and ![absolute](https://www.find.com/image.png)",
            [
                MarkdownLinkRuleResult(
                    full="![relative image](../image1.png)",
                    text="relative image",
                    url="../image1.png",
                ),
                MarkdownLinkRuleResult(
                    full="![absolute](https://www.find.com/image.png)",
                    text="absolute",
                    url="https://www.find.com/image.png",
                ),
            ],
        ),
    ]
)


@pytest.mark.parametrize("data", data)
def test_MarkdownDocument_image_links(create_markdown_file, data):

    links = data

    md = MarkdownDocument(create_markdown_file)

    assert md.image_links == links


data = []

data.append(
    [
        LinkLineNumber(
            1,
            "Here is an image: ![relative image](../image1.png) and ![absolute](https://www.find.com/image.png)",
            [
                MarkdownLinkRuleResult(
                    full="![relative image](../image1.png)",
                    text="relative image",
                    url="../image1.png",
                ),
                MarkdownLinkRuleResult(
                    full="![absolute](https://www.find.com/image.png)",
                    text="absolute",
                    url="https://www.find.com/image.png",
                ),
            ],
        ),
        LinkLineNumber(
            8,
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
            10,
            "5 Test 1 - [basic](./test.md) line",
            [
                MarkdownLinkRuleResult(
                    full="[basic](./test.md)",
                    text="basic",
                    url="./test.md",
                )
            ],
        ),
        LinkLineNumber(
            15,
            "# [web](http://www.python.org) and [local](../md.txt)",
            [
                MarkdownLinkRuleResult(
                    full="[web](http://www.python.org)",
                    text="web",
                    url="http://www.python.org",
                ),
                MarkdownLinkRuleResult(
                    full="[local](../md.txt)",
                    text="local",
                    url="../md.txt",
                ),
            ],
        ),
    ]
)


@pytest.mark.parametrize("data", data)
def test_MarkdownDocument_all_links(create_markdown_file, data):

    links = data

    md = MarkdownDocument(create_markdown_file)

    assert md.all_links == links


data = []

data.append(
    [
        LinkLineNumber(
            1,
            "Here is an image: ![relative image](../image1.png) and ![absolute](https://www.find.com/image.png)",
            [
                MarkdownLinkRuleResult(
                    full="![relative image](../image1.png)",
                    text="relative image",
                    url="../image1.png",
                ),
            ],
        ),
        LinkLineNumber(
            10,
            "5 Test 1 - [basic](./test.md) line",
            [
                MarkdownLinkRuleResult(
                    full="[basic](./test.md)",
                    text="basic",
                    url="./test.md",
                )
            ],
        ),
        LinkLineNumber(
            15,
            "# [web](http://www.python.org) and [local](../md.txt)",
            [
                MarkdownLinkRuleResult(
                    full="[local](../md.txt)",
                    text="local",
                    url="../md.txt",
                ),
            ],
        ),
    ]
)


@pytest.mark.parametrize("data", data)
def test_MarkdownDocument_all_relative_links(create_markdown_file, data):

    links = data

    md = MarkdownDocument(create_markdown_file)

    assert md.all_relative_links == links
