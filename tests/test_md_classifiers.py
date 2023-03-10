#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2020 Troy Williams

uuid       = 0469cb3e-3007-11eb-bf3c-ab85e03a1801
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2020-11-26
-----------

"""

import pytest

from md_tools.markdown_classifiers import (
    MarkdownLinkRuleResult,
    MarkdownLinkRule,
    MarkdownImageLinkRuleResult,
    MarkdownImageLinkRule,
    HTMLImageLinkRuleResult,
    HTMLImageLinkRule,
    RelativeURLRuleResult,
    RelativeURLRule,
    AbsoluteURLRuleResult,
    AbsoluteURLRule,
    CodeFenceRuleResult,
    CodeFenceRule,
    YamlBlockRule,
    DirectiveStringRuleResult,
    DirectiveStringRule,
)

# -------------
# Test - MarkdownLinkRule - matches


data = []

data.append(
    (
        "- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.",
        True,
    )
)
data.append(
    (
        "The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.",
        True,
    )
)
data.append(("## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)", True))
data.append(
    (
        "The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)",
        True,
    )
)
data.append(("[Hyperbola](../../assets/HyperbolaAnatomyLeft.png)", True))
data.append(("[Definition of a circular arc.](../assets/circle_arc.png)", True))

data.append(("This string does not contain any links", False))
data.append(
    (
        "This string does not contain any links, only image an image: ![image](./image.png)",
        False,
    )
)


@pytest.mark.parametrize("data", data)
def test_MarkdownLinkRule_match(data):
    value, result = data
    rule = MarkdownLinkRule()
    assert rule(value) == result


data = []
data.append(("This string does not contain any links", None))

data.append(
    (
        "- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.",
        [
            MarkdownLinkRuleResult(
                text="pandoc-fignos",
                url="https://github.com/tomduck/pandoc-fignos",
                full="[pandoc-fignos](https://github.com/tomduck/pandoc-fignos)",
            )
        ],
    )
)

data.append(
    (
        "## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)",
        [
            MarkdownLinkRuleResult(
                text="Equations",
                url="./ch0_2_equations.md#sec:ch0_2_equations-1",
                full="[Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)",
            )
        ],
    )
)

data.append(
    (
        "The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.",
        [
            MarkdownLinkRuleResult(
                text="figure",
                url="./ch0_1_images.md#fig:ch0_1_images-1",
                full="[figure](./ch0_1_images.md#fig:ch0_1_images-1)",
            ),
            MarkdownLinkRuleResult(
                text="figure",
                url="./ch0_1_images.md#fig:ch0_1_images-2",
                full="[figure](./ch0_1_images.md#fig:ch0_1_images-2)",
            ),
        ],
    )
)

data.append(
    (
        "The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)",
        [
            MarkdownLinkRuleResult(
                text="internal energy equation",
                url="./ch0_2_equations.md#eq:ch0_2_equations-1",
                full="[internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1)",
            ),
            MarkdownLinkRuleResult(
                text="detonation pressure",
                url="./ch0_2_equations.md#eq:ch0_2_equations-2",
                full="[detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)",
            ),
        ],
    )
)


@pytest.mark.parametrize("data", data)
def test_MarkdownLinkRule_result(data):
    value, results = data
    rule = MarkdownLinkRule()

    rule(value)
    assert rule.result == results


# --------------
# Test MarkdownImageRule


data = []

data.append(
    (
        "- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.",
        False,
    )
)
data.append(
    (
        "The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.",
        False,
    )
)
data.append(("## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)", False))
data.append(
    (
        "The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)",
        False,
    )
)
data.append(("This string does not contain any links", False))


data.append(("![Caption.](image.png){#fig:id}", True))
data.append(('![Caption.](image.png){#fig:id tag="B.1"}', True))
data.append(
    (
        "![This is a sample image representing the VOD curve of a packaged Watergel explosive.](../assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png){#fig:ch0_1_images-1 width=100%}",
        True,
    )
)
data.append(
    ("![](../../assets/E5WnRoSH_Dqrzl8f5_ZJ9AjWc-53BgiBqD_xTqEp6pM=.png)", True)
)
data.append(
    (
        "![](../../assets/XwMrG0o__iLF5nStoSPUuJ81ffxafRBWAVnEcGo10Yo=.png) and another image: ![test](image.png)",
        True,
    )
)


@pytest.mark.parametrize("data", data)
def test_MarkdownImageLinkRule_match(data):
    value, result = data
    rule = MarkdownImageLinkRule()

    assert rule(value) == result


data = []
data.append(
    (
        "- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.",
        None,
    )
)
data.append(
    (
        "The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.",
        None,
    )
)
data.append(("## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)", None))
data.append(
    (
        "The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)",
        None,
    )
)
data.append(("This string does not contain any links", None))

data.append(
    (
        "![Caption.](image.png){#fig:id}",
        [
            MarkdownImageLinkRuleResult(
                full="![Caption.](image.png)",
                text="Caption.",
                url="image.png",
            ),
        ],
    )
)


data.append(
    (
        '![Caption.](image.png){#fig:id tag="B.1"}',
        [
            MarkdownImageLinkRuleResult(
                full="![Caption.](image.png)",
                text="Caption.",
                url="image.png",
            ),
        ],
    )
)


data.append(
    (
        "![This is a sample image representing the VOD curve of a packaged Watergel explosive.](../assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png){#fig:ch0_1_images-1 width=100%}",
        [
            MarkdownImageLinkRuleResult(
                full="![This is a sample image representing the VOD curve of a packaged Watergel explosive.](../assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png)",
                text="This is a sample image representing the VOD curve of a packaged Watergel explosive.",
                url="../assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png",
            ),
        ],
    )
)

data.append(
    (
        "![](../../assets/E5WnRoSH_Dqrzl8f5_ZJ9AjWc-53BgiBqD_xTqEp6pM=.png)",
        [
            MarkdownImageLinkRuleResult(
                full="![](../../assets/E5WnRoSH_Dqrzl8f5_ZJ9AjWc-53BgiBqD_xTqEp6pM=.png)",
                text="",
                url="../../assets/E5WnRoSH_Dqrzl8f5_ZJ9AjWc-53BgiBqD_xTqEp6pM=.png",
            ),
        ],
    )
)

data.append(
    (
        "![This Image](image1.png) and another image ![That Image](image2.png)",
        [
            MarkdownImageLinkRuleResult(
                full="![This Image](image1.png)",
                text="This Image",
                url="image1.png",
            ),
            MarkdownImageLinkRuleResult(
                full="![That Image](image2.png)",
                text="That Image",
                url="image2.png",
            ),
        ],
    )
)


@pytest.mark.parametrize("data", data)
def test_MarkdownImageLinkRule_results(data):
    value, results = data
    rule = MarkdownImageLinkRule()

    rule(value)
    assert rule.result == results


# --------------
# Test HTMLImageLinkRule

data = []

data.append(
    (
        '<img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>',
        True,
    )
)
data.append(
    (
        '<img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>',
        True,
    )
)
data.append(
    (
        '<img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/> ',
        True,
    )
)
data.append(('<img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>', True))

data.append(('<img src="hello world"/> <img /> <img src="hello world"/>', True))

data.append(('<img alt="Similar Triangles" style="width: 600px;"/>', False))
data.append(("<img/>", False))


@pytest.mark.parametrize("data", data)
def test_html_image_rule_match(data):
    question, answer = data
    rule = HTMLImageLinkRule()

    assert rule(question) == answer


data = []

data.append(
    (
        '<img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>',
        [
            HTMLImageLinkRuleResult(
                full='<img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>',
                src="../../assets/similar_triangles.png",
            ),
        ],
    )
)
data.append(
    (
        '<img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>',
        [
            HTMLImageLinkRuleResult(
                full='<img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>',
                src="../../assets/break_out_angle.png",
            ),
        ],
    )
)
data.append(
    (
        '<img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>',
        [
            HTMLImageLinkRuleResult(
                full='<img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>',
                src="azimuth_dump.png",
            ),
        ],
    )
)
data.append(
    (
        '<img src="hello world"/> <img /> <img src="hello world2"/>',
        [
            HTMLImageLinkRuleResult(
                full='<img src="hello world"/>',
                src="hello world",
            ),
            HTMLImageLinkRuleResult(
                full='<img src="hello world2"/>',
                src="hello world2",
            ),
        ],
    )
)

data.append(('<img alt="Similar Triangles" style="width: 600px;"/>', None))
data.append(("<img/>", None))


@pytest.mark.parametrize("data", data)
def test_html_image_rule_extraction(data):
    question, answer = data
    rule = HTMLImageLinkRule()

    rule(question)

    assert rule.result == answer


# ----
# Relative URLs


data = []
data.append(("https://github.com/tomduck/pandoc-fignos", False))
data.append(("http://github.com/tomduck/pandoc-fignos", False))
data.append(("ftp://github.com/tomduck/pandoc-fignos", False))
data.append(("ftp://github.com/ tomduck/ pandoc-fignos", False))
data.append(("ftp:// github.com/ tomduck/ pandoc-fignos", False))
data.append(("ftps://github.com/tomduck/pandoc-fignos", False))

data.append(("www.google.ca", True))
data.append(("google.com", True))


data.append(("./ch0_1_images.md#fig:ch0_1_images-1", True))
data.append(("./ch0_1_images.md#fig:ch0_1_images-2", True))
data.append(("./ch0_2_equations.md#sec:ch0_2_equations-1", True))
data.append(("./ch0_2_equations.md#eq:ch0_2_equations-1", True))
data.append(("./ch0_2_equations.md#eq:ch0_2_equations-2", True))
data.append(("./ch0_2_equations.md", True))
data.append(("./hello world.md", True))
data.append(("#eq:ch0_2_equations-2", True))
data.append(("#eq:ch0_2_equations-2", True))
data.append(("../assets/circle_arc.png", True))
data.append(("../../assets/HyperbolaAnatomyLeft.png", True))


@pytest.mark.parametrize("data", data)
def test_RelativeURLRule_match(data):
    value, result = data
    rule = RelativeURLRule()

    assert rule(value) == result


data = []
data.append(("https://github.com/tomduck/pandoc-fignos", None))
data.append(("http://github.com/tomduck/pandoc-fignos", None))
data.append(("ftp://github.com/tomduck/pandoc-fignos", None))
data.append(("ftp://github.com/ tomduck/ pandoc-fignos", None))
data.append(("ftp:// github.com/ tomduck/ pandoc-fignos", None))
data.append(("ftps://github.com/tomduck/pandoc-fignos", None))


data.append(
    (
        "./ch0_1_images.md#fig:ch0_1_images-1",
        RelativeURLRuleResult(
            file="./ch0_1_images.md",
            section="#fig:ch0_1_images-1",
        ),
    )
)

data.append(
    (
        "./ch0_1_images.md#fig:ch0_1_images-2",
        RelativeURLRuleResult(
            file="./ch0_1_images.md",
            section="#fig:ch0_1_images-2",
        ),
    )
)

data.append(
    (
        "./ch0_2_equations.md",
        RelativeURLRuleResult(
            file="./ch0_2_equations.md",
            section=None,
        ),
    )
)


data.append(
    (
        "#eq:ch0_2_equations-2",
        RelativeURLRuleResult(
            file="",
            section="#eq:ch0_2_equations-2",
        ),
    )
)


@pytest.mark.parametrize("data", data)
def test_RelativeURLRule_result(data):
    value, results = data
    rule = RelativeURLRule()

    rule(value)
    assert rule.result == results


# ----------
# Test AbsoluteURLRule


data = []

data.append(("https://github.com/tomduck/pandoc-fignos", True))
data.append(("http://github.com/tomduck/pandoc-fignos", True))
data.append(("ftp://github.com/tomduck/pandoc-fignos", True))

data.append(("http://github.com/ tomduck/ pandoc-fignos", False))
data.append(("ftp:// github.com/ tomduck/ pandoc-fignos", False))
data.append(("ftps://github.com/tomduck/pandoc-fignos", False))
data.append(("www.google.ca", False))
data.append(("google.com", False))


@pytest.mark.parametrize("data", data)
def test_absolute_url_rule_match(data):
    value, result = data
    rule = AbsoluteURLRule()

    assert rule(value) == result


data = []
data.append(
    (
        "https://github.com/tomduck/pandoc-fignos",
        AbsoluteURLRuleResult(url="https://github.com/tomduck/pandoc-fignos"),
    )
)
data.append(
    (
        "http://github.com/tomduck/pandoc-fignos",
        AbsoluteURLRuleResult(url="http://github.com/tomduck/pandoc-fignos"),
    )
)
data.append(
    (
        "ftp://github.com/tomduck/pandoc-fignos",
        AbsoluteURLRuleResult(url="ftp://github.com/tomduck/pandoc-fignos"),
    )
)

data.append(("http://github.com/ tomduck/ pandoc-fignos", None))
data.append(("ftp:// github.com/ tomduck/ pandoc-fignos", None))
data.append(("ftps://github.com/tomduck/pandoc-fignos", None))
data.append(("www.google.ca", None))
data.append(("google.com", None))


@pytest.mark.parametrize("data", data)
def test_absolute_url_rule_extraction(data):
    value, results = data
    rule = AbsoluteURLRule()

    rule(value)

    assert rule.result == results


# ----------------
# Test - CodeFenceClassifier

data = []

# ```   bash hello world
# ``` bash hello world
# ~~~    python
# ~~~
# ```
#                         ```````` hello

data.append(("```   bash hello world", True))
data.append(("``` bash hello world", True))
data.append(("~~~", True))
data.append(("     ~~~   ", True))
data.append(("```", True))
data.append(("```    ", True))
data.append(("```    python", True))
data.append(("     ```    python", True))
data.append(("     ``````    python", True))
data.append(("  ~~~~    python", True))
data.append(("```````python", True))

data.append(("     ``~`    python", False))
data.append(("     `~~`    python", False))
data.append(("     ``~`    python", False))


@pytest.mark.parametrize("data", data)
def test_CodeFenceRule_match(data):
    value, result = data
    rule = CodeFenceRule()

    assert rule(value) == result

data = []
data.append(("```   bash hello world", True))
data.append(("``` bash hello world", True))
data.append(("~~~", False))
data.append(("     ~~~   ", False))
data.append(("```", True))
data.append(("```    ", True))
data.append(("```    python", True))
data.append(("     ```    python", True))
data.append(("     ``````    python", True))
data.append(("  ~~~~    python", False))
data.append(("```````python", True))

data.append(("     ``~`    python", False))
data.append(("     `~~`    python", False))
data.append(("     ``~`    python", False))


@pytest.mark.parametrize("data", data)
def test_CodeFenceRule_match(data):
    value, result = data
    rule = CodeFenceRule(backticks_only=True)

    assert rule(value) == result



data = []

data.append(
    (
        "```   bash hello world",
        CodeFenceRuleResult(
            arguments="bash hello world",
        ),
    )
)

data.append(
    (
        "``` bash hello world",
        CodeFenceRuleResult(
            arguments="bash hello world",
        ),
    )
)


data.append(
    (
        "```    {admonition}    This is my admonition",
        CodeFenceRuleResult(
            arguments="{admonition}    This is my admonition",
        ),
    )
)


data.append(
    (
        "```    {admonition}    This is my admonition      ",
        CodeFenceRuleResult(
            arguments="{admonition}    This is my admonition",
        ),
    )
)

data.append(
    (
        "~~~",
        CodeFenceRuleResult(
            arguments="",
        ),
    )
)

data.append(
    (
        "     ~~~   ",
        CodeFenceRuleResult(
            arguments="",
        ),
    )
)

data.append(
    (
        "```",
        CodeFenceRuleResult(
            arguments="",
        ),
    )
)


data.append(
    (
        "```    ",
        CodeFenceRuleResult(
            arguments="",
        ),
    )
)

data.append(
    (
        "```    python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)

data.append(
    (
        "     ```    python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)

data.append(
    (
        "     ``````    python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)


data.append(
    (
        "  ~~~~    python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)

data.append(
    (
        "```````python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)

data.append(("     ``~`    python", None))
data.append(("     `~~`    python", None))
data.append(("     ``~`    python", None))


@pytest.mark.parametrize("data", data)
def test_CodeFenceRule_result(data):
    value, result = data
    rule = CodeFenceRule()

    rule(value)
    assert rule.result == result


data = []

data.append(
    (
        "```   bash hello world",
        CodeFenceRuleResult(
            arguments="bash hello world",
        ),
    )
)

data.append(
    (
        "``` bash hello world",
        CodeFenceRuleResult(
            arguments="bash hello world",
        ),
    )
)


data.append(
    (
        "```    {admonition}    This is my admonition",
        CodeFenceRuleResult(
            arguments="{admonition}    This is my admonition",
        ),
    )
)


data.append(
    (
        "```    {admonition}    This is my admonition      ",
        CodeFenceRuleResult(
            arguments="{admonition}    This is my admonition",
        ),
    )
)

data.append(
    (
        "~~~",
        None,
    )
)

data.append(
    (
        "     ~~~   ",
        None,
    )
)

data.append(
    (
        "```",
        CodeFenceRuleResult(
            arguments="",
        ),
    )
)


data.append(
    (
        "```    ",
        CodeFenceRuleResult(
            arguments="",
        ),
    )
)

data.append(
    (
        "```    python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)

data.append(
    (
        "~~~    python",
        None,
    )
)

data.append(
    (
        "     ```    python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)

data.append(
    (
        "     ``````    python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)


data.append(
    (
        "  ~~~~    python",
        None,
    )
)

data.append(
    (
        "```````python",
        CodeFenceRuleResult(
            arguments="python",
        ),
    )
)

data.append(("     ``~`    python", None))
data.append(("     `~~`    python", None))
data.append(("     ``~`    python", None))



@pytest.mark.parametrize("data", data)
def test_CodeFenceRule_result(data):
    value, result = data
    rule = CodeFenceRule(backticks_only=True)

    rule(value)
    assert rule.result == result


# ----------------
# Test - YamlBlockClassifier

data = []

# ---   <- Valid Start or End
# ...   <- Valid End

data.append(("---", True))
data.append(("...", True))


data.append(("--- ", True))
data.append(("... ", True))
data.append(("---   ", True))
data.append(("...  ", True))

data.append(("c++", False))
data.append(("c--", False))
data.append(("c==", False))
data.append(("dee", False))
data.append(("  --- ", False))
data.append(("  ... ", False))


@pytest.mark.parametrize("data", data)
def test_YamlBlockRule_result(data):
    value, result = data
    rule = YamlBlockRule()

    assert rule(value) == result


# ----------------
# Test - DirectiveStringRule

data = []


data.append(("   ```text", False))
data.append(("```````python", False))
data.append(("  ~~~~    python", False))
data.append(("     ``````    python", False))
data.append((" python", False))
data.append(("   python", False))
data.append(("python rocks", False))
data.append(("admonition}    This is my admonition", False))
data.append(("```{admonition}", False))


data.append(("{admonition}",True))
data.append(("{admonition}  hello world",True))
data.append(("   {admonition}  hello world",True))
data.append(("{admonition} This is my admonition",True))
data.append(("    {admonition}    This is my admonition",True))



@pytest.mark.parametrize("data", data)
def test_DirectiveStringRule_match(data):
    value, result = data
    rule = DirectiveStringRule()

    assert rule(value) == result


data = []

data.append(
    (
        "{admonition}",
        DirectiveStringRuleResult(
            directivename="admonition",
            arguments="",
        ),
    )
)

data.append(
    (
        "{admonition}  hello world",
        DirectiveStringRuleResult(
            directivename="admonition",
            arguments="hello world",
        ),
    )
)

data.append(
    (
        "   {admonition}  hello world",
        DirectiveStringRuleResult(
            directivename="admonition",
            arguments="hello world",
        ),
    )
)


data.append(
    (
        "   {admonition}  hello world    ",
        DirectiveStringRuleResult(
            directivename="admonition",
            arguments="hello world",
        ),
    )
)


data.append(
    (
        "{admonition}      hello world",
        DirectiveStringRuleResult(
            directivename="admonition",
            arguments="hello world",
        ),
    )
)


data.append(
    (
        " python",
        None,
    )
)

data.append(
    (
        " python  ",
        None,
    )
)

data.append(
    (
        "```{admonition}      hello world",
        None,
    )
)


@pytest.mark.parametrize("data", data)
def test_DirectiveStringRule_result(data):
    value, result = data
    rule = DirectiveStringRule()

    rule(value)
    assert rule.result == result






# # ----------
# # ATXHeaderRule - ATX level 1

# data = []
# data.append(("# Test", True))
# data.append(("# Hello World", True))
# data.append(("# #Admin - Test", True))

# data.append(("# Hello World", True))
# data.append((" # Hello World", True))
# data.append(("  # Hello World", True))
# data.append(("   # Hello World", True))
# data.append(("    # Hello World", False))
# data.append(("     # Hello World", False))


# data.append(("    # Test     ", False))
# data.append((" ## Test", False))
# data.append(("Hello # Test", False))
# data.append(("## Test", False))


# @pytest.mark.parametrize("data", data)
# def test_atxheader_rule_1(data):

#     key = "Hello asdfasdf"
#     value, result = data
#     rule = ATXHeaderRule(key=key, count=1)

#     assert rule.key == key
#     assert rule.match(value) == result
#     assert rule.match(value) == result  # test memoization
#     assert rule.is_full_match == False


# # ---------
# # Test - ATXHeaderRule - 2

# data = []
# data.append(("## Test", True))
# data.append(("## Hello World", True))
# data.append(("## #Admin - Test", True))
# data.append((" ## Test", True))

# data.append(("    ## Test     ", False))
# data.append(("Hello ## Test", False))
# data.append(("### Test", False))
# data.append(("# Test", False))


# @pytest.mark.parametrize("data", data)
# def test_atxheader_rule_2(data):

#     key = "Hello asdfasdf"
#     value, result = data
#     rule = ATXHeaderRule(key=key, count=2)

#     assert rule.key == key
#     assert rule.match(value) == result
#     assert rule.match(value) == result  # test memoization
#     assert rule.is_full_match == False


# # ---------
# # Test - ATXHeaderRule - 3

# data = []
# data.append(("### Test", True))
# data.append(("### Hello World", True))
# data.append(("### #Admin - Test", True))
# data.append((" ### Test", True))

# data.append(("    ### Test     ", False))
# data.append(("Hello ### Test", False))
# data.append(("#### Test", False))
# data.append(("## Test", False))


# @pytest.mark.parametrize("data", data)
# def test_atxheader_rule_3(data):

#     key = "Hello asdfasdf"
#     value, result = data
#     rule = ATXHeaderRule(key=key, count=3)

#     assert rule.key == key
#     assert rule.match(value) == result
#     assert rule.match(value) == result  # test memoization
#     assert rule.is_full_match == False


# # ---------
# # Test - ATXHeaderRule - 4

# data = []
# data.append(("#### Test", True))
# data.append(("#### Hello World", True))
# data.append(("#### #Admin - Test", True))
# data.append((" #### Test", True))

# data.append(("    #### Test     ", False))
# data.append(("Hello #### Test", False))
# data.append(("##### Test", False))
# data.append(("### Test", False))


# @pytest.mark.parametrize("data", data)
# def test_atxheader_rule_4(data):

#     key = "Hello asdfasdf"
#     value, result = data
#     rule = ATXHeaderRule(key=key, count=4)

#     assert rule.key == key
#     assert rule.match(value) == result
#     assert rule.match(value) == result  # test memoization
#     assert rule.is_full_match == False


# # ---------
# # Test - ATXHeaderRule - 5

# data = []
# data.append(("##### Test", True))
# data.append(("##### Hello World", True))
# data.append(("##### #Admin - Test", True))
# data.append((" ##### Test", True))

# data.append(("    ##### Test     ", False))
# data.append(("Hello ##### Test", False))
# data.append(("###### Test", False))
# data.append(("#### Test", False))


# @pytest.mark.parametrize("data", data)
# def test_atxheader_rule_5(data):

#     key = "Hello asdfasdf"
#     value, result = data
#     rule = ATXHeaderRule(key=key, count=5)

#     assert rule.key == key
#     assert rule.match(value) == result
#     assert rule.match(value) == result  # test memoization
#     assert rule.is_full_match == False


# # ---------
# # Test - ATXHeaderRule - 6

# data = []
# data.append(("###### Test", True))
# data.append(("###### Hello World", True))
# data.append(("###### #Admin - Test", True))
# data.append((" ###### Test", True))

# data.append(("    ###### Test     ", False))
# data.append(("Hello ###### Test", False))
# data.append(("####### Test", False))
# data.append(("##### Test", False))


# @pytest.mark.parametrize("data", data)
# def test_atxheader_rule_6(data):

#     key = "Hello asdfasdf"
#     value, result = data
#     rule = ATXHeaderRule(key=key, count=6)

#     assert rule.key == key
#     assert rule.match(value) == result
#     assert rule.match(value) == result  # test memoization
#     assert rule.is_full_match == False


# # ---------
# # Test - ATXHeaderRule - exception


# def test_atxheader_rule_error():

#     key = "Hello asdfasdf"

#     with pytest.raises(ValueError):
#         rule = ATXHeaderRule(key=key, count=0)

#     with pytest.raises(ValueError):
#         rule = ATXHeaderRule(key=key, count=7)

#     with pytest.raises(ValueError):
#         rule = ATXHeaderRule(key=key, count=-1)


# # -----------
# # Test - ATXHeaderRule - 1 - Extract Data

# data = []
# data.append(("# Test", "Test"))
# data.append(("# Hello World", "Hello World"))
# data.append(("# #Admin - Test", "#Admin - Test"))

# data.append(("    # Test     ", None))
# data.append((" ## Test", None))
# data.append(("Hello # Test", None))
# data.append(("## Test", None))


# @pytest.mark.parametrize("data", data)
# def test_atxheader_rule_1_data(data):

#     key = "Hello asdfasdf"
#     value, result = data
#     rule = ATXHeaderRule(key=key, count=1)

#     assert rule.key == key

#     assert rule.extract_data(value) == result
#     assert rule.extract_data(value) == result  # test memoization

#     assert rule.is_full_match == False
