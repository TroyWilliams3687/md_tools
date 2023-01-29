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

from md_tools.markdown import find_atx_header

from md_tools.markdown import (
    extract_markdown_links,
    # extract_relative_markdown_links,
    extract_markdown_image_links,
    # extract_relative_markdown_image_links,
)


from md_tools.markdown_classifiers import (
    MarkdownLinkRuleResult,
    RelativeMarkdownURLRuleResult,
)

# -----------
# Test find_atx_header

data = []
data.append(("# Header Level 1", "Header Level 1"))
data.append(("## Header Level 2", "Header Level 2"))
data.append(("### Header Level 3", "Header Level 3"))
data.append(("#### Header Level 4", "Header Level 4"))
data.append(("##### Header Level 5", "Header Level 5"))
data.append(("###### Header Level 6", "Header Level 6"))

data.append(("# # Header Level 2", "# Header Level 2"))
data.append(("## # Header Level 3", "# Header Level 3"))
data.append(("### # Header Level 4", "# Header Level 4"))
data.append(("#### # Header Level 5", "# Header Level 5"))
data.append(("##### # Header Level 6", "# Header Level 6"))

data.append((" # Header Level 1", "Header Level 1"))
data.append(("  ## Header Level 2", "Header Level 2"))
data.append(("   ### Header Level 3", "Header Level 3"))

data.append(("Not a header", None))
data.append(("$# Not a header", None))
data.append(("     #### Header Level 4 - Too many leading spaces", None))


@pytest.mark.parametrize("data", data)
def test_find_atx_header(data):

    tv, tr = data

    result = find_atx_header(tv)

    if result:
        level, text, line_number = result
        assert text == tr

    else:
        assert result == tr


# ----------
# extract_markdown_links

data = []

lines = []
results = []

data.append(
    (
        "This is a link [test](https://www.google.ca)",
        [
            MarkdownLinkRuleResult(
                full= "[test](https://www.google.ca)",
                text= "test",
                url= "https://www.google.ca",
                relative=None,
            ),
        ],
    )
)


data.append(
    (
        "This is a link another [link](./local/file.text)",
        [
            MarkdownLinkRuleResult(
                full="[link](./local/file.text)",
                text="link",
                url="./local/file.text",
                relative=RelativeMarkdownURLRuleResult(
                    full="./local/file.text",
                    md="./local/file.text",
                    section=None,
                ),
            ),
        ],
    )
)

data.append(
    (
        "This is a link [test](https://www.google.ca) and another [link](./local/file.text)",

        [
            MarkdownLinkRuleResult(
                full= "[test](https://www.google.ca)",
                text= "test",
                url= "https://www.google.ca",
                relative=None,
            ),
            MarkdownLinkRuleResult(
                full="[link](./local/file.text)",
                text="link",
                url="./local/file.text",
                relative=RelativeMarkdownURLRuleResult(
                    full="./local/file.text",
                    md="./local/file.text",
                    section=None,
                ),
            ),
        ],
    )
)

data.append(
    (
     "Here is a test link: [Equations](http://test.org/ch0_2_equations.html#sec:ch0_2_equations-1).",
     [
        MarkdownLinkRuleResult(
                 full= "[Equations](http://test.org/ch0_2_equations.html#sec:ch0_2_equations-1)",
                 text= "Equations",
                 url= "http://test.org/ch0_2_equations.html#sec:ch0_2_equations-1",
             ),
    ],
    )
)

data.append(
    (
     "Here is a another one:  [Images](./ch0_1_images.html#sec:ch0_1_images-1)!",
     [
        MarkdownLinkRuleResult(
                 full= "[Images](./ch0_1_images.html#sec:ch0_1_images-1)",
                 text= "Images",
                 url= "./ch0_1_images.html#sec:ch0_1_images-1",
                 relative=RelativeMarkdownURLRuleResult(
                        full="./ch0_1_images.html#sec:ch0_1_images-1",
                        md="./ch0_1_images.html",
                        section="#sec:ch0_1_images-1",
                ),
        ),
    ],
    )
)



@pytest.mark.parametrize("data", data)
def test_extract_markdown_links(data):
    line, compare = data

    results = extract_markdown_links(line)

    assert len(compare) == len(results)

    for c, r in zip(compare, results):
        assert c == r



# # ----------
# # extract_markdown_image_links

data = []

data.append((
    "Here is an image link: ![Image Caption](http://www.url.test/image.png)",
    [
        MarkdownLinkRuleResult(
             full= "![Image Caption](http://www.url.test/image.png)",
             text= "Image Caption",
             url= "http://www.url.test/image.png",
         ),
    ],
))


data.append((
    "Here is another image link -> ![](./assets/image.png)",
    [
        MarkdownLinkRuleResult(
                 full= "![](./assets/image.png)",
                 text= "",
                 url= "./assets/image.png",
                 relative=RelativeMarkdownURLRuleResult(
                        full="./assets/image.png",
                        md="./assets/image.png",
                        section=None,
                ),
        ),
    ],
))



@pytest.mark.parametrize("data", data)
def test_extract_markdown_image_links(data):

    line, compare = data

    results = extract_markdown_image_links(line)

    assert len(compare) == len(results)

    for c, r in zip(compare, results):
        assert c == r



