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
"""

# ------------
# System Modules - Included with Python

import re

from abc import ABC, abstractmethod, abstractproperty
from typing import Optional, NamedTuple, Generator

# ------------

# 2023-01-30
# - Rebuild the rules


# https://docs.python.org/3/library/typing.html#typing.NamedTuple <- The way to define a `typed` namedtuple


class MarkdownLinkRuleResult(NamedTuple):
    """
    The result from the MarkdownLinkBaseRule.

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


class MarkdownLinkBaseRule(ABC):
    """
    Match tokens within a text string using regex and return the
    results, if any, as a MarkdownLinkRuleResult object.
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
    def result(self) -> Optional[list[MarkdownLinkRuleResult]]:
        """
        The list of MarkdownLinkRuleResult matching the regex
        """
        return self._result

    def _search_text(self, text: str = None) -> list[MarkdownLinkRuleResult]:
        """
        Search the text for matches contructing a list of
        MarkdownLinkRuleResult objects
        """

        return [
            MarkdownLinkRuleResult(
                full=m.group(),
                text=m.group("text"),
                url=m.group("url"),
            )
            for m in self._regex.finditer(text)
        ]

    def __call__(self, text: str = None) -> bool:
        """
        Does the text contain Markdown links?

        If it does, use the result attribute to access the matches.
        """
        result = self._search_text(text)

        self._result = result if len(result) > 0 else None

        return self._result is not None


class MarkdownTokenLinkRule(MarkdownLinkBaseRule):
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


class MarkdownImageTokenLinkRule(MarkdownLinkBaseRule):
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


class HTMLImageRuleResult(NamedTuple):
    """
    Given a string:

    `<img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>`

    It will return a match identifying:

    full - <img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>
    src -  ../../assets/similar_triangles.png

    """

    full: str
    src: str


class HTMLImageRule(MarkdownLinkBaseRule):
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

    # def __init__(self, **kwargs):

    #     self._build_regex()
    #     self._result = None

    def _build_regex(self):

        self._regex = re.compile(
            r"<img\s+[^>]*src=\"(?P<src>[^\"]*)\"[^>]*>",
        )

    @property
    def result(self) -> Optional[HTMLImageRuleResult]:
        """
        The list of links that matched the last selection.
        """
        return self._result

    def _search_text(self, text: str = None) -> list[HTMLImageRuleResult]:
        """
        Search the text for matches constructing a list of
        HTMLImageRuleResult objects
        """
        return [
            HTMLImageRuleResult(
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

    full: str
    infostring: Optional[str]


class CodeFenceRule:
    """
    Examines the line to see if it matches the code block ``` or ~~~


    - Contains at least 3 backticks, ` or 3 tildes
    - cannot be mixed backticks and tildes
    - can be as many leading spaces before the code fence
    - can have an info string following the code fence
    - the infostring is the first word after the opening of the code
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
            r"^\s*(?:`{3,}|~{3,})\s*(?P<infostring>\w*).*$",
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


# # ------------
# # ------------
# # ------------

# # The stuff below works.

# class RelativeMarkdownURLRuleResult(NamedTuple):
#     """
#     # https://docs.python.org/3/library/typing.html#typing.NamedTuple <- The way to define a `typed` namedtuple

#     The result of a RelativeMarkdownURLRule match

#     full-  Full text match
#     md - The string representing the link.
#     section - The string representing the section anchor, if any.
#     md_span -  A tuple(start, end) Containing the starting and ending position of the markdown link match in the string
#     section_span - A tuple(start, end) Containing the starting and ending position of the section anchor match in the string

#     """
#     full:str
#     md:str
#     section:str
#     # md_span:tuple[int,int]
#     # section_span:tuple[int,int]


# class MarkdownLinkRuleResult(NamedTuple):
#     """
#     # https://docs.python.org/3/library/typing.html#typing.NamedTuple <- The way to define a `typed` namedtuple

#     The result of a MarkDownLineRule match

#     full-  Full text match
#     text- Link description Text
#     link- URL

#     """
#     full: str
#     text: str
#     url: str
#     relative:Optional[RelativeMarkdownURLRuleResult] = None


# # class MarkdownImageRuleResult(NamedTuple):
# #     """
# #     # https://docs.python.org/3/library/typing.html#typing.NamedTuple <- The way to define a `typed` namedtuple

# #     The result of a MarkDownLineRule match

# #     full-  Full text match
# #     caption- The image caption portion of the link -> ![image caption](URL)
# #     url- URL to the image

# #     """
# #     full: str
# #     caption: str
# #     url: str
# #     relative:Optional[RelativeMarkdownURLRuleResult] = None


# # ----
# class MatchRule(ABC):
#     """
#     This is an abstract base class used to define a string matching
#     rule.

#     Given a string, it applies a regex based criteria to the string to
#     find a match. If a match is found, True is returned otherwise
#     False. The rule will also provide a way to extract the match data -
#     if relevant.

#     NOTE: This is only a line/string based criteria match. It should
#     only produce a True or False statement

#     NOTE: This is from my notes application and is copyright TBW but
#     under an MIT license.
#     """

#     def __init__(self, **kwargs):
#         """

#         # Parameters (kwargs)

#         key: str
#             - A reference key to identify this rule
#         """

#         self.kwargs = kwargs

#         self.key = kwargs["key"] if "key" in kwargs else None

#         # have a rule that indicates if the rule is active
#         self.disabled = False

#         # memoization - store the match results keyed by string
#         self.cache_results = {}

#         self.regex = None

#         self._build_regex()

#     def _get_match_result(self, line:str):
#         """
#         This method will run the line through the regex_matcher function
#         and return the results.

#         If the results are cached for the specific line, they are
#         returned, otherwise the results are calculated, cached and
#         returned.

#         # Parameters

#         line: str
#             - The string to classify

#         # Return

#         The return item depends on the concrete implementation of the
#         _find_results method.

#         """

#         result = None

#         if line in self.cache_results:
#             result = self.cache_results[line]

#         else:
#             result = self._find_result(line)
#             self.cache_results[line] = result

#         return result

#     @abstractmethod
#     def _build_regex(self):
#         """
#         A method to construct the regular expression used by the
#         classifier rule.
#         """
#         pass

#     @abstractproperty
#     def is_full_match(self):
#         """
#         A Rule can apply partially to a line or to the entire line. This
#         property when True indicates that this rule will match an
#         entire line.

#         If it is false, it can partially match a line.

#         The idea is to iterate through a iterable of lines
#         (str), applying the rules to each line. If a rule matches, this
#         property is checked. If this property is True, there is no
#         point checking the rest of the rules as it is not possible for
#         them to match the line further.

#         In other words, the rule is True if it is not possible
#         (or doesn't make sense) to apply other rules to the line.

#         # NOTE

#         This defines the getter for the system. Simply return True or
#         False depending on the rule. This value should not be altered
#         once the object is instantiated.

#         """

#         pass

#     @abstractmethod
#     def _find_result(self, line):
#         """
#         Given the line, find the matches.
#         """
#         pass

#     @abstractmethod
#     def match(self, line):
#         """
#         Apply the rule to the line and return a boolean value. If the
#         line matches the rule, True is returned, otherwise False.

#         # Parameters

#         line: str
#             - The string to evaluate against the matching rule.

#         # Note

#         We are only interested in a boolean result. There is no need for
#         complex calculations or conversions in this method. It should
#         be relatively light weight.

#         """

#         pass

#     @abstractmethod
#     def extract_data(self, line, **kwargs):
#         """
#         Apply the rule to the line and return the extracted data in the
#         expected form.

#         # Parameters

#         line: str
#             - The string to evaluate against the matching rule.

#         # Return

#         The return value(s) highly depends on the concrete
#         implementation.

#         """

#         pass


# class MarkdownLinkRule(MatchRule):
#     """
#     Examines the markdown line for valid markdown links. If the line
#     contains one or more links, it is considered a match.


#     # Markdown Link

#     A markdown link is of the form [descriptive text](URL link). There
#     can be multiple links within a line.

#     ```
#     - [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers
#       figures and figure references.

#     The images section will walk you through how to add and reference
#     images so that the pandoc system can properly number them. For
#     example, this [figure]
#     (./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for
#     a packaged watergel explosive and this [figure]
#     (./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.

#     ## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)

#     The equations section will discuss how to use equations and
#     reference them properly. See the [internal energy equation]
#     (./ch0_2_equations.md#eq:ch0_2_equations-1) or the
#     [detonation pressure]
#     (./ch0_2_equations.md#eq:ch0_2_equations-2)
#     ```

#     """

#     def _build_regex(self):
#         """
#         Construct the regex that will match the markdown formatted links
#         in the line.
#         """

#         # use negative look behind - The regex has to be like this
#         # otherwise it'll capture too far if we don't have the
#         # non-greedy option
#         local_regex = r"(?<!!)(?:\[(?P<text>.*?)\]\((?P<url>.*?)\))"

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self):
#         """
#         This rule doesn't match the full string, so other rules can be
#         applied to the same line of text.
#         """

#         return False

#     def _find_result(self, line):
#         """ """

#         result = [
#             MarkdownLinkRuleResult(
#                 full=m.group(),
#                 text=m.group("text"),
#                 url=m.group("url"),
#             )
#             for m in self.regex.finditer(line)
#         ]

#         return result if len(result) > 0 else None

#     def match(self, line):
#         """
#         If the line matches, True is returned.
#         """

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line:str, **kwargs) -> Optional[list[MarkdownLinkRuleResult]]:
#         """
#         Attempts to extract the information from the line if there is a
#         match. If there is no match, None is returned.

#         # Return

#         A match will return a list of MarkdownLinkRuleResult objects
#         that contain the 'text' of the link and the 'link' URL and the
#         `full` markdown match.

#         If no match is found, None is returned
#         """

#         return self._get_match_result(line)


# # ----------------
# # Match Standard URL in markdown links:
# # regex -> r"(?:\[.*?\])\((?P<url>(?:https?|ftp)://.*?)\)"

# # - [pandoc-fignos](https://github.com/tomduck/pandoc-fignos) <- Match
# # - [pandoc-fignos](http://github.com/tomduck/pandoc-fignos) <- Match
# # - [pandoc-fignos](ftp://github.com/tomduck/pandoc-fignos) <- Match
# # - [pandoc-fignos](ftps://github.com/tomduck/pandoc-fignos) <- NO Match

# # NOTE: I don't think this is required....
# # -----------------


# class AbsoluteURLRule(MatchRule):
#     """

#     This rule will match an absolute URL of the form:

#     - https://github.com/tomduck/pandoc-fignos   <- Match
#     - http://github.com/tomduck/pandoc-fignos    <- Match
#     - ftp://github.com/tomduck/pandoc-fignos     <- Match
#     - http://github.com/ tomduck/ pandoc-fignos  <- No Match
#     - ftp:// github.com/ tomduck/ pandoc-fignos  <- No Match
#     - ftps://github.com/tomduck/pandoc-fignos    <- No Match
#     - www.google.ca                              <- No Match
#     - google.com                                 <- No Match

#     # Assumptions

#     - It looks for the protocol://
#     - Assumes the whole string is the URL, from start to finish
#     - Not designed to search in text for URL

#     Not a match if:

#     - Contains spaces
#     - Missing protocol
#     - Unrecognized protocol

#     # Note

#     This rule is designed to match the entire string. For this rule to
#     work effectively the string should have already been classified by
#     the MarkDownLinkRule

#     - https://regex101.com/r/u1tn0I/8

#     """

#     def _build_regex(self):
#         """
#         Construct and cache the regex.
#         """

#         local_regex = r"^(?P<url>(?:https?|ftp)://\S*)$"

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self):
#         """
#         If the rule matches, there is no point applying other rules to
#         the string.

#         In this case, this rule is meant to match the entire string.
#         """

#         return True

#     def _find_result(self, line):
#         """ """

#         result = self.regex.match(line)

#         return result

#     def match(self, line):
#         """
#         If the string matches the regex, True is returned.
#         """

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line, **kwargs):
#         """ """

#         result = self._get_match_result(line)

#         if result:
#             return result.group("url")

#         else:
#             return None


# class RelativeMarkdownURLRule(MatchRule):
#     """

#     This rule will match an relative URL of the
#     form: "./ch0_1_images.md#fig:ch0_1_images-1"

#     - https://github.com/tomduck/pandoc-fignos       <- not a Match
#     - http://github.com/tomduck/pandoc-fignos        <- not a Match
#     - ftp://github.com/tomduck/pandoc-fignos         <- not a Match
#     - ftp://github.com/ tomduck/ pandoc-fignos       <- not a Match
#     - ftp:// github.com/ tomduck/ pandoc-fignos      <- not a Match
#     - ftps://github.com/tomduck/pandoc-fignos        <- not a Match
#     - www.google.ca                                  <- not a Match
#     - google.com                                     <- not a Match
#     - ./ch0_1_images.md#fig:ch0_1_images-1           <- Match
#     - ./ch0_1_images.md#fig:ch0_1_images-2           <- Match
#     - ./ch0_2_equations.md#sec:ch0_2_equations-1     <- Match
#     - ./ch0_2_equations.md#eq:ch0_2_equations-1      <- Match
#     - ./ch0_2_equations.md#eq:ch0_2_equations-2      <- Match
#     - ./ch0_2_equations.md                           <- Match
#     - ./hello world.md                               <- Match
#     - #eq:ch0_2_equations-2                          <- Match
#     - #eq:ch0_2_equations-2                          <- Match

#     - ../assets/circle_arc.png                       <- Match
#     - ../../assets/HyperbolaAnatomyLeft.png          <- Match

#     # Assumptions

#     - It ignores the protocol://
#     - It has to contain a reference to a .md file or section '#'
#     - The whole string is the URL
#     - Empty strings will not be checked

#     Not a match if:

#     - Contains protocol://
#     - Empty
#     - missing .md, .png, jpg, jpeg, gif
#     - missing '#'

#     # Note

#     This rule is designed to match the entire string. For this rule to
#     work effectively the string should have already been classified by
#     the MarkDownLinkRule

#     - https://regex101.com/r/u1tn0I/10

#     """

#     def _build_regex(self):
#         """
#         Construct and cache the regex.
#         """

#         local_regex = r"^(?!.*:\/\/)(?P<md>[^#]*?)(?P<section>#.*)?$"

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self):
#         """
#         If the rule matches, there is no point applying other rules to
#         the string.

#         In this case, this rule is meant to match the entire string.
#         """

#         return True

#     def _find_result(self, line):
#         """ """

#         result = self.regex.match(line)

#         if result:
#             return RelativeMarkdownURLRuleResult(
#                 full=result.group(),
#                 md=result.group("md"),
#                 section=result.group("section"),
#                 # md_span=result.span("md"),
#                 # section_span=result.span("section"),
#             )


#             # return {
#             #     "full": result.group(),
#             #     "md_span": result.span(
#             #         "md"
#             #     ),  # tuple(start, end) <- start and end position of the match
#             #     "md": result.group("md"),
#             #     "section_span": result.span("section"),
#             #     "section": result.group("section"),
#             # }

#         else:
#             return None

#     def match(self, line):
#         """
#         If the string matches the regex, True is returned.
#         """

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line, **kwargs):
#         """ """

#         return self._get_match_result(line)


# # ---------
# # Markdown Image Links


# class MarkdownImageRule(MatchRule):
#     """
#     This rule can be used to examine lines of text for markdown image
#     links. It can also extract the data from the markdown image links.


#     # Markdown Image link

#     A markdown image link is of the form ![descriptive text](URL link).
#     There can be multiple links within a line.

#     ```
#     These don't match:
#     - [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers
#       figures and figure references. The images section will walk you
#       through how to add and reference images so that the pandoc system
#       can properly number them. For example, this [figure]
#       (./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve
#       for a packaged watergel explosive and this [figure]
#       (./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.
#     ## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1) The
#        equations section will discuss how to use equations and
#        reference them properly. See the [internal energy equation]
#        (./ch0_2_equations.md#eq:ch0_2_equations-1) or the
#        [detonation pressure]
#        (./ch0_2_equations.md#eq:ch0_2_equations-2) This string does not
#        contain any links


#     These Match:
#     ![Caption.](image.png){#fig:id}
#     ![Caption.](image.png){#fig:id tag="B.1"}
#     ![This is a sample image representing the VOD curve of a packaged
#      Watergel explosive.]
#      (../assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png)
#      {#fig:ch0_1_images-1 width=100%}
#     ![](../../assets/E5WnRoSH_Dqrzl8f5_ZJ9AjWc-53BgiBqD_xTqEp6pM=.png)
#     ![](../../assets/l2mxAo3IR1dc3Wrgt7Ulqhcm_8nwqFw5UY7pUI3X0oI=.png)
#     ![](../../assets/Y7jjv0ceQH5Ew5O32U2Z_N7ARBfKn2FnHnUoUt_DYbA=.png)
#     ![](../../assets/eOvy-JcdA7pjoDJS4rIgG5RgDfYJ4PY11Owbgy5DHWM=.png)
#     ![](../../assets/XwMrG0o__iLF5nStoSPUuJ81ffxafRBWAVnEcGo10Yo=.png)
#     ```

#     """

#     def _build_regex(self):
#         """
#         Construct the regex that will match the markdown image links in
#         the line.
#         """

#         local_regex = r"(?:[!]\[(?P<caption>.*?)\])\((?P<url>.*?)\)"

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self):
#         """
#         This rule doesn't match the full string, so other rules can be
#         applied to the same line of text.
#         """

#         return False

#     def _find_result(self, line):
#         """ """

#         result = [
#             MarkdownLinkRuleResult(
#                 full=m.group(),
#                 text=m.group("caption"),
#                 url=m.group("url"),
#             )
#             for m in self.regex.finditer(line)
#         ]

#         return result if len(result) > 0 else None

#     def match(self, line):
#         """
#         True is returned if the regex finds a match in the line of text.
#         """

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line, **kwargs):
#         """
#         Attempts to extract the information from the line if there is a
#         match. If there is no match, None is returned.

#         # Return

#         A match will return a list of dictionaries that contain
#         the 'caption' and the 'image' URL.

#         [{'caption':'image caption', 'image':'URL'}]

#         If no match is found, None is returned

#         """

#         return self._get_match_result(line)


# class HTMLImageRule(MatchRule):
#     """
#     This rule can be used to examine lines of text for html image links.
#     Specifically, it is interested in img links that have the src
#     attribute set and can return that.

#     The image link is of the form:

#     - <img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>
#     - <img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>
#     - <img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>
#     - <img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>

#     <img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/> <- match
#     <img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>     <- match
#     <img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>     <- match
#     <img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>                             <- match
#     <img src="hello world"/> <img /> <img src="hello world"/>                                     <- match, no-match, match
#     <img alt="Similar Triangles" style="width: 600px;"/>                                          <- no-match
#     <img/>                                                                                        <- no-match

#     ```

#     """

#     def _build_regex(self):
#         """
#         Construct the regex that will match the HTML image links in the
#         line.
#         """

#         local_regex = r"<img\s+[^>]*src=\"(?P<src>[^\"]*)\"[^>]*>"

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self):
#         """
#         This rule doesn't match the full string, so other rules can be
#         applied to the same line of text.
#         """

#         return False

#     def _find_result(self, line):
#         """ """

#         result = [
#             {
#                 "full": m.group(),
#                 "src": m.group("src"),
#             }
#             for m in self.regex.finditer(line)
#         ]

#         return result if len(result) > 0 else None

#     def match(self, line):
#         """
#         True is returned if the regex finds a match in the line of text.
#         """

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line, **kwargs):
#         """
#         Attempts to extract the information from the line if there is a
#         match. If there is no match, None is returned.

#         {'full':data, 'src':data}

#         """

#         return self._get_match_result(line)


# class ATXHeaderRule(MatchRule):
#     """
#     Examines the line to see if it matches the definition of an ATX
#     header in markdown.

#     # Section One

#     ## Section Two

#     ### Section Three

#     #### four

#     ##### five

#     ###### six

#     [Definitions](https://spec.commonmark.org/0.24/#atx-headings):

#     - It starts with an octothorpe
#     - It can have up to 6 octothorpes (commonmark)
#     - There can be up to 3 spaces before the start of the ATX Heading
#     - There is at least 1 space after the last octothrope and the text

#     # Reference

#     https://spec.commonmark.org/0.24/#atx-headings


#     """

#     def __init__(self, **kwargs):
#         """

#         # Parameters (kwargs)

#         key: str
#             - The reference key to identify this rule

#         count: int
#             - The level of ATX header to match (1 - 6)

#         """

#         self.atx_count = kwargs["count"] if "count" in kwargs else 1

#         if self.atx_count < 1 or self.atx_count > 6:
#             raise ValueError(
#                 f"Out of range for count = {self.atx_count}. It has to be between 1 and 6."
#             )

#         # call super init last because it will call the _build_regex
#         # method
#         super().__init__(**kwargs)

#     def _build_regex(self):
#         """
#         Construct the regex that will match the markdown formatted links
#         in the line.
#         """

#         # # Hello World   <- match
#         #  # Hello World  <- match
#         #   # Hello World <- match
#         #    # Hello World <- no match
#         #     # Hello World <- no match
#         #      # Hello World <- no match

#         local_regex = r"(?:^\s{{0,3}}\#{{{0}}}\s+)(?P<title>.*)$".format(self.atx_count)

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self):
#         """
#         This rule doesn't match the full string, so other rules can be
#         applied to the same line of text.
#         """

#         return False

#     def _find_result(self, line):
#         """ """

#         result = self.regex.match(line)

#         if result:
#             return result.group("title")

#         else:
#             return None

#     def match(self, line):
#         """
#         True is returned if the regex finds a match in the line of text.
#         """

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line, **kwargs):
#         """
#         Attempts to extract the information from the line if there is a
#         match. If there is no match, None is returned.

#         # Return

#         A match will return the title text.

#         If no match is found, None is returned

#         """
#         return self._get_match_result(line)


# class MarkdownAttributeSyntax(MatchRule):
#     """
#     Looks for any attribute syntax in the markdown line. We are
#     interested in the id portion which should be the first hashtag
#     item: {#index-section-01}. This will return 'index-section-01'

#     ```
#     # Header 1 {#header_1 .sidebar}

#     ## Header 2 {#header_2 .topbar}

#     ![image](./path/to/image.png) {#image_1 .image_link}

#     ![image](./path/to/image.png) {.image_link #image_1}

#     # Header 1 { #header_1 .sidebar}

#     ## Header 2 {        #header_2 .topbar}

#     ![image](./path/to/image.png) {xxx     #image_1 .image_link}

#     ```

#     """

#     def _build_regex(self):
#         """
#         Construct the regex that will match the markdown formatted links
#         in the line.

#         """

#         local_regex = r"(?:\{(?:.*)(?:\#)(?P<id>\S+)(?:.*)\})"  # can change \S for \w

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self):
#         """
#         This rule doesn't match the full string, so other rules can be
#         applied to the same line of text.
#         """

#         return False

#     def _find_result(self, line):
#         """ """

#         result = [
#             {"full": m.group(), "id": m.group("id")} for m in self.regex.finditer(line)
#         ]

#         return result if len(result) > 0 else None

#     def match(self, line):
#         """
#         If the line matches, True is returned.
#         """

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line, **kwargs):
#         """
#         Attempts to extract the information from the line if there is a
#         match. If there is no match, None is returned.

#         # Return

#         A match will return a list of dictionaries that contain
#         the 'text' of the link and the 'link' URL.

#         [{'full': 'full match', 'id':'Link description Text'}]

#         If no match is found, None is returned

#         """

#         return self._get_match_result(line)


# # Find Code Fence


# class CodeFenceClassifier(MatchRule):
#     """
#     Examines the line to see if it matches the code block ``` or ~~~


#     - Contains at least 3 backticks, ` or 3 tildes
#     - cannot be mixed backticks and tildes
#     - can be as many leading spaces before the code fence
#     - can have an info string following the code fence
#     - the infostring is the first word after the opening of the code
#       fence
#     - can have as many spaces as is needed after the code fence and
#       before the info string
#     - the end of the document closes the code fence automatically

#     ``` ruby

#     # Some ruby code here

#     ```

#     ```python

#     # Some python code in here

#     ```

#     https://spec.commonmark.org/0.29/#fenced-code-blocks

#     """

#     def _build_regex(self):

#         # Captures the following:
#         # ```   bash hello world
#         # ``` bash hello world
#         # ~~~    python
#         # ~~~
#         # ```
#         #                         ```````` hello

#         local_regex = r"^\s*(?:`{3,}|~{3,})\s*(?P<infostring>\w*).*$"

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self) -> bool:

#         return True

#     def _find_result(self, line):
#         """ """

#         result = [
#             {"full": m.group(), "infostring": m.group("infostring")}
#             for m in self.regex.finditer(line)
#         ]

#         return result if len(result) > 0 else None

#     def match(self, line: str) -> bool:

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line: str, **kwargs) -> str:

#         return self._get_match_result(line)


# # Find YAML Block


# class YamlBlockClassifier(MatchRule):
#     """
#     A YAML metadata block is a valid YAML object, delimited by a line of
#     three hyphens (---) at the top and a line of three hyphens (---) or
#     three dots (...) at the bottom.

#     - Contains at least 3 hyphens, - or 3 dots .
#     - cannot be mixed hyphens and dots
#     - can be as many leading spaces before the block
#     - the end of the document closes the block fence automatically

#     ---
#     # Yaml data
#     ID: xyz-1
#     version: 12
#     ...

#     """

#     def _build_regex(self):

#         local_regex = r"^(-{3}|\.{3})\s*$"

#         self.regex = re.compile(local_regex)

#     @property
#     def is_full_match(self) -> bool:

#         return True

#     def _find_result(self, line):
#         """ """

#         result = [
#             {
#                 "full": m.group(),
#             }
#             for m in self.regex.finditer(line)
#         ]

#         return result if len(result) > 0 else None

#     def match(self, line: str) -> bool:

#         result = self._get_match_result(line)

#         return result is not None

#     def extract_data(self, line: str, **kwargs) -> str:

#         return self._get_match_result(line)


# class MDFence:
#     """
#     A simple object to wrap up tests to see if we are in code blocks or
#     YAML blocks. We can't be in both at the same time.

#     # Usage

#     ```
#     ignore_block = MDFence()

#     for line in contents:

#         if ignore_block.in_block(line):
#             continue

#         # The line isn't part of a code fence or YAML block. Process it.

#     ```

#     """

#     def __init__(self):
#         """ """
#         self.code_rule = CodeFenceClassifier()
#         self.yaml_rule = YamlBlockClassifier()

#         self.in_block_type = {
#             "code": False,
#             "yaml": False,
#         }

#     def in_block(self, line):
#         """ """

#         if self.in_block_type["code"]:

#             # Are we at the end?
#             if self.code_rule.match(line):
#                 self.in_block_type["code"] = False

#             # We are at the last line of the code block, but caller
#             # would consider this line still in the block. We return
#             # True, but we have set the flag to false

#             return True

#         if self.in_block_type["yaml"]:

#             # Are we at the end?
#             if self.yaml_rule.match(line):
#                 self.in_block_type["yaml"] = False

#             # We are at the last line of the code block, but caller
#             # would consider this line still in the block. We return
#             # True, but we have set the flag to false

#             return True

#         # If we made it this far, we are not in a code block. Check to
#         # see if we are entering one

#         # Have we entered a code block?
#         if self.code_rule.match(line):

#             self.in_block_type["code"] = True

#             return True

#         # Have we entered a YAML block?
#         if self.yaml_rule.match(line):

#             self.in_block_type["yaml"] = True

#             return True

#         return False
