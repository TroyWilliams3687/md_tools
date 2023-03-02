#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Troy Williams

# uuid:   61db24ca-3007-11eb-bf3c-ab85e03a1801
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date:   2020-11-26
# -----------

"""
Contains custom rules for classifying/matching markdown elements within
a string representing a line in a markdown file.

This contains the most basic line oriented operations and matching rules.

"""

# ------------
# System Modules - Included with Python

import re

from abc import ABC, abstractmethod, abstractproperty
from typing import Optional, NamedTuple
from collections.abc import Sequence

# ------------

# 2023-01-30
# - Rebuild the rules


# https://docs.python.org/3/library/typing.html#typing.NamedTuple <- The way to define a `typed` namedtuple


class TokenRule(ABC):
    """
    An abstract base class for rules that can return 0 or more
    results. It is used as the base class for rules that can match
    multiple items within a string.
    """

    def __init__(self, **kwargs):
        self._build_regex()
        self._result = None

    @abstractmethod
    def _build_regex(self):
        """
        A method to construct the regular expression used by the
        classifier rule.
        """
        pass

    @property
    def result(self) -> Optional[Sequence]:
        """
        The list of MarkdownLinkRuleResult matching the regex

        NOTE: __call__ must be called before results are stored.

        NOTE: if __call__ will overwrite results
        """
        return self._result

    @abstractmethod
    def _search_text(self, text: str = None) -> Sequence:
        """
        Search the text for matches returning a Sequence of results.
        """

        pass

    def __call__(self, text: str = None) -> bool:
        """
        Call the object like a function returning a boolean if the
        tokens are found.

        NOTE: This must be called before calling result.
        """
        result = self._search_text(text)

        self._result = result if len(result) > 0 else None

        return self._result is not None


class MarkdownLinkRuleResult(NamedTuple):
    """
    The result from the MarkdownLinkRule.

    [test link](https://www.bluebill.net/test1)

    https://www.ibm.com/docs/en/cics-ts/5.1?topic=concepts-components-url
    https://host:port/path#section

    full - Full text match - `[test link](https://www.bluebill.net/test1)`
    text - Link description Text - `test link`
    link - URL - `https://www.bluebill.net/test1`

    relative - a reference to the relative link rule result.

    """

    full: str
    text: str
    url: str


class MarkdownLinkRule(TokenRule):
    """
    Determine if the text contains Markdown formatted hyperlinks.

    [test link](https://www.bluebill.net/test1)

    The caller can then access the result attribute for a list of
    MarkdownLinkRuleResult objects.
    """

    def _build_regex(self):
        """
        A method to construct the regular expression used by the
        classifier rule.
        """

        self._regex = re.compile(
            r"(?<!!)(?:\[(?P<text>.*?)\]\((?P<url>.*?)\))",
        )

    def _search_text(self, text: str = None) -> Sequence[MarkdownLinkRuleResult]:
        return [
            MarkdownLinkRuleResult(
                full=m.group(),
                text=m.group("text"),
                url=m.group("url"),
            )
            for m in self._regex.finditer(text)
        ]


class MarkdownImageLinkRuleResult(NamedTuple):
    """
    The result from the MarkdownLinkRule.

    [test link](https://www.bluebill.net/test1)

    https://www.ibm.com/docs/en/cics-ts/5.1?topic=concepts-components-url
    https://host:port/path#section

    full - Full text match - `[test link](https://www.bluebill.net/test1)`
    text - Link description Text - `test link`
    link - URL - `https://www.bluebill.net/test1`

    relative - a reference to the relative link rule result.

    """

    full: str
    text: str
    url: str


class MarkdownImageLinkRule(TokenRule):
    """
    Determine if the text contains Markdown formatted image links.

    ![An Image](https://www.bluebill.net/test1/image.png)

    The caller can then access the result attribute for a list of
    MarkdownLinkRuleResult objects.
    """

    def _build_regex(self):
        """
        A method to construct the regular expression used by the
        classifier rule.
        """

        self._regex = re.compile(
            r"(?:[!]\[(?P<text>.*?)\])\((?P<url>.*?)\)",
        )

    def _search_text(self, text: str = None) -> Sequence[MarkdownImageLinkRuleResult]:
        return [
            MarkdownImageLinkRuleResult(
                full=m.group(),
                text=m.group("text"),
                url=m.group("url"),
            )
            for m in self._regex.finditer(text)
        ]


class HTMLImageLinkRuleResult(NamedTuple):
    """
    Given a string:

    `<img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>`

    It will return a match identifying:

    full - <img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>
    src -  ../../assets/similar_triangles.png

    """

    full: str
    src: str


class HTMLImageLinkRule(TokenRule):
    """
    This rule can be used to examine lines of text for html image links.
    Specifically, it is interested in img links that have the src
    attribute set and can return that.

    The image link is of the form:

    - <img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>
    - <img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>
    - <img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>
    - <img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>

    <img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/> <- match
    <img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>     <- match
    <img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>     <- match
    <img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>                             <- match
    <img src="hello world"/> <img /> <img src="hello world"/>                                     <- match, no-match, match
    <img alt="Similar Triangles" style="width: 600px;"/>                                          <- no-match
    <img/>                                                                                        <- no-match
    """

    def _build_regex(self):
        self._regex = re.compile(
            r"<img\s+[^>]*src=\"(?P<src>[^\"]*)\"[^>]*>",
        )

    def _search_text(self, text: str = None) -> Sequence[HTMLImageLinkRuleResult]:
        """
        Search the text for matches constructing a list of
        HTMLImageLinkRuleResult objects
        """
        return [
            HTMLImageLinkRuleResult(
                full=m.group(),
                src=m.group("src"),
            )
            for m in self._regex.finditer(text)
        ]


class RelativeURLRuleResult(NamedTuple):
    """
    Given a string:

    `./ch0_1_images.md#fig:ch0_1_images-1`

    It will return a match identifying the file and the section.

    file = ./ch0_1_images.md
    section = #fig:ch0_1_images-1

    """

    file: str
    section: Optional[str]


class RelativeURLRule:
    """
    This rule will match an relative URL of the
    form:

    `./ch0_1_images.md#fig:ch0_1_images-1`

    - https://github.com/tomduck/pandoc-fignos       <- not a Match
    - http://github.com/tomduck/pandoc-fignos        <- not a Match
    - ftp://github.com/tomduck/pandoc-fignos         <- not a Match
    - ftp://github.com/ tomduck/ pandoc-fignos       <- not a Match
    - ftp:// github.com/ tomduck/ pandoc-fignos      <- not a Match
    - ftps://github.com/tomduck/pandoc-fignos        <- not a Match
    - www.google.ca                                  <- not a Match
    - google.com                                     <- not a Match
    - ./ch0_1_images.md#fig:ch0_1_images-1           <- Match
    - ./ch0_1_images.md#fig:ch0_1_images-2           <- Match
    - ./ch0_2_equations.md#sec:ch0_2_equations-1     <- Match
    - ./ch0_2_equations.md#eq:ch0_2_equations-1      <- Match
    - ./ch0_2_equations.md#eq:ch0_2_equations-2      <- Match
    - ./ch0_2_equations.md                           <- Match
    - ./hello world.md                               <- Match
    - #eq:ch0_2_equations-2                          <- Match
    - #eq:ch0_2_equations-2                          <- Match

    - ../assets/circle_arc.png                       <- Match
    - ../../assets/HyperbolaAnatomyLeft.png          <- Match

    # Assumptions

    - It ignores the protocol://
    - It has to contain a reference to a file or section '#'
    - The whole string is the URL
    - Empty strings will not be checked

    Not a match if:

    - Contains protocol://
    - Empty

    # Note

    This rule is designed to match the entire string. For this rule to
    work effectively the string should have already been classified by
    the MarkDownLinkRule

    - https://regex101.com/r/u1tn0I/10
    """

    def __init__(self, **kwargs):
        self._build_regex()
        self._result = None

    def _build_regex(self):
        self._regex = re.compile(
            r"^(?!.*:\/\/)(?P<file>[^#]*?)(?P<section>#.*)?$",
        )

    @property
    def result(self) -> Optional[RelativeURLRuleResult]:
        """
        The list of links that matched the last selection.
        """
        return self._result

    def __call__(self, text: str = None) -> bool:
        """
        Does the text contain Markdown links?
        """
        m = self._regex.match(text)

        self._result = RelativeURLRuleResult(**m.groupdict()) if m is not None else None

        return self._result is not None


class AbsoluteURLRuleResult(NamedTuple):
    """
    Given a string:

    `https://github.com/tomduck/pandoc-fignos `

    It will return a match identifying the URL

    url = https://github.com/tomduck/pandoc-fignos

    """

    url: str


class AbsoluteURLRule:
    """

    This rule will match an absolute URL of the form:

    - https://github.com/tomduck/pandoc-fignos   <- Match
    - http://github.com/tomduck/pandoc-fignos    <- Match
    - ftp://github.com/tomduck/pandoc-fignos     <- Match
    - http://github.com/ tomduck/ pandoc-fignos  <- No Match
    - ftp:// github.com/ tomduck/ pandoc-fignos  <- No Match
    - ftps://github.com/tomduck/pandoc-fignos    <- No Match
    - www.google.ca                              <- No Match
    - google.com                                 <- No Match

    # Assumptions

    - It looks for the protocol://
    - Assumes the whole string is the URL, from start to finish
    - Not designed to search in text for URL

    Not a match if:

    - Contains spaces
    - Missing protocol
    - Unrecognized protocol

    # Note

    This rule is designed to match the entire string. For this rule to
    work effectively the string should have already been classified by
    the MarkDownLinkRule

    - https://regex101.com/r/u1tn0I/8

    """

    def __init__(self, **kwargs):
        self._build_regex()
        self._result = None

    def _build_regex(self):
        self._regex = re.compile(
            r"^(?P<url>(?:https?|ftp)://\S*)$",
        )

    @property
    def result(self) -> Optional[AbsoluteURLRuleResult]:
        """
        The list of links that matched the last selection.
        """
        return self._result

    def __call__(self, text: str = None) -> bool:
        """
        Does the text contain Markdown links?
        """
        m = self._regex.match(text)

        self._result = AbsoluteURLRuleResult(**m.groupdict()) if m is not None else None

        return self._result is not None


class CodeFenceRuleResult(NamedTuple):
    """ """

    arguments: Optional[str]


class CodeFenceRule:
    """
    Examines the line to see if it matches the code block ``` or ~~~


    - Contains at least 3 backticks, ` or 3 tildes
    - cannot be mixed backticks and tildes
    - can be as many leading spaces before the code fence
    - can have an info string following the code fence
    - the arguments are the words after the opening of the code
      fence
    - can have as many spaces as is needed after the code fence and
      before the info string
    - the end of the document closes the code fence automatically

    ``` ruby

    # Some ruby code here

    ```

    ```python

    # Some python code in here

    ```

    https://spec.commonmark.org/0.29/#fenced-code-blocks

    """

    def __init__(self, **kwargs):
        self._build_regex()
        self._result = None

    def _build_regex(self):
        self._regex = re.compile(
            r"^\s*(?:`{3,}|~{3,})(?:\s*)(?P<arguments>.*?)(?:\s*)$",
        )

    @property
    def result(self) -> Optional[AbsoluteURLRuleResult]:
        """
        The list of links that matched the last selection.
        """
        return self._result

    def __call__(self, text: str = None) -> bool:
        """
        Does the text contain Markdown links?
        """
        m = self._regex.match(text)

        self._result = CodeFenceRuleResult(**m.groupdict()) if m is not None else None

        return self._result is not None


class YamlBlockRule:
    """
    A YAML metadata block is a valid YAML object, delimited by a line of
    three hyphens (---) at the top and a line of three hyphens (---) or
    three dots (...) at the bottom.

    - Contains at least 3 hyphens, - or 3 dots .
    - cannot be mixed hyphens and dots
    - can be as many leading spaces before the block
    - the end of the document closes the block fence automatically

    ---
    # Yaml data
    ID: xyz-1
    version: 12
    ...

    """

    def __init__(self, **kwargs):
        self._regex = re.compile(
            r"^(-{3}|\.{3})\s*$",
        )

    def __call__(self, text: str = None) -> bool:
        """
        Does the text contain Markdown links?
        """
        m = self._regex.match(text)
        return m is not None
