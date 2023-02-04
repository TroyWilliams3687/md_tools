#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams

# uuid   = e2414710-a00e-11ed-9662-89c2b25e0fa7
# author = Troy Williams
# email  = troy.williams@bluebill.net
# date   = 2023-01-29
# -----------

"""
"""

# ------------
# System Modules - Included with Python

import re

from collections.abc import Sequence, Generator
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Optional, NamedTuple


# ------------
# 3rd Party - From PyPI

# ------------
# Custom Modules

from .markdown_classifiers import (
    MarkdownLinkRuleResult,
    MarkdownTokenLinkRule,
    MarkdownImageTokenLinkRule,
    HTMLImageRuleResult,
    HTMLImageRule,
    RelativeURLRuleResult,
    RelativeURLRule,
    AbsoluteURLRuleResult,
    AbsoluteURLRule,
    CodeFenceRuleResult,
    CodeFenceRule,
    YamlBlockRule,
    # AbsoluteURLRule,
    # ATXHeaderRule,
    # MarkdownAttributeSyntax,
    # MarkdownImageRule,
    # MarkdownLinkRule,
    # MDFence,
    # RelativeMarkdownURLRule,
    # MarkdownLinkRuleResult,
    # RelativeMarkdownURLRuleResult,
)
# -------------

class MDFence:
    """
    This object keeps track of whether we are iterating through a fence
    block(code block or YAML block) while iterating through a markdown
    string.

    # Usage

    ```
    ignore_block = MDFence()

    for line in contents:

        if ignore_block.in_block(line):
            continue

        # The line isn't part of a code fence or YAML block. Process it.
    ```

    """

    def __init__(self):

        self.fence_types = ("code", "yaml")

        rules = (CodeFenceRule(), YamlBlockRule())
        self.rules = dict(zip(self.fence_types, rules))

        self.in_fence = dict(zip(self.fence_types, (False,False)))

    def __call__(self, line:str=None) -> bool:

        # Are we in a block?
        for bt in self.fence_types:

            if self.in_fence[bt]:

                # Are we at the end?
                if self.rules[bt](line):
                    self.in_fence[bt] = False

                # We are at the last line of the fence block, but caller
                # would consider this line still in the block. We return
                # True, but we have set the flag to false

                return True


        # Have we entered a fence block?
        for bt in self.fence_types:

            if self.rules[bt](line):
                self.in_fence[bt] = True

                return True

        # We are not in a fence block
        return False



class LineNumber(NamedTuple):
    """
    Represents the individual lines within a sequence of strings.

    number - the line number within the sequence of strings
    line - the line itself
    """

    number:int
    line:str


def outside_fence(lines:Optional[Sequence[str]]=None, start:int=0) -> Generator[LineNumber, None, None]:
    """
    This method will iterate through the lines in the sequence, skipping
    any that are within fence blocks (YAML or code blocks).

    # Parameters

    lines - a sequence of strings

    start - the start of the sequence to use for the line numbers.
        - Default = 0

    # Return

    A LineNumber object representing the line number and the string that
    isn't inside a fence block..
    """

    if lines is None:
        return  # this is effectively raising a StopIteration

    in_block = MDFence()

    for i, line in enumerate(lines, start=start):

        if in_block(line):
            continue

        yield LineNumber(i, line)



class LinkLineNumber(NamedTuple):
    """
    Represents the individual lines within a sequence of strings.

    number - the line number within the sequence of strings
    line - the line itself
    """

    number:int
    line:str
    matches:Optional[Sequence[MarkdownLinkRuleResult]]


def markdown_links(lines:Optional[Sequence[str]]=None, start:int=0) -> Generator[LinkLineNumber, None, None]:
    """
    This method will return lines that contain markdown links.

    # Parameters

    lines - a sequence of strings

    start - the start of the sequence to use for the line numbers.
        - Default = 0

    # Return

    A LinkLineNumber object representing the line number and the string
    that contains markdown links as well as the actual matches.

    """

    rule = MarkdownTokenLinkRule()

    for valid_line in outside_fence(lines, start=start):

        if rule(valid_line.line):

            yield LinkLineNumber(*valid_line, matches=rule.result)




# generator - extract markdown image links





# ----
# ----
# ----
# ----


# def extract_markdown_links(line: str) -> Optional[list[MarkdownLinkRuleResult]]:
#     """

#     Given a line, return all of the markdown links. The markdown links
#     will be of the form:

#     (Description)[URL]

#     (This is a link)[../file.md#section_title]

#     This method will return a list of link dictionaries for each link
#     found in the line.

#     # Parameters

#     line - The text string to analyze for markdown links

#     # Return

#     Assume that the markdown link looks like this in the text:
#     - (Description)[URL]
#     - (This is a link)[../file.md#section_title]
#     - [text](link)

#     This method will return a list of MarkdownLinkRuleResult objects
#     with the following attributes:

#     - `full` - The full regex match - [text](link)
#     - `text` - The text portion of the markdown link
#     - `link` - The URL portion of the markdown link

#     # Note

#     The line classifier rules perform memoization and should be
#     instantiated above the loop that calls this method. I don't expect
#     many duplicate lines so this optimization is not necessary. Mostly
#     it is about the match and the extract data

#     """

#     link_rule = MarkdownLinkRule()
#     relative_rule = RelativeMarkdownURLRule()

#     matches = []

#     if link_rule.match(line.strip()):

#         for r in link_rule.extract_data(line.strip()):

#             link = MarkdownLinkRuleResult(
#                 full=r.full,
#                 text=r.text,
#                 url=r.url,
#             )

#             if relative_rule.match(r.url):

#                 link = MarkdownLinkRuleResult(
#                     full=link.full,
#                     text=link.text,
#                     url=link.url,
#                     relative=relative_rule.extract_data(r.url),
#                 )

#             matches.append(link)

#     return matches


# def extract_relative_markdown_links(line:str, **kwargs) -> Optional[list[MarkdownLinkRuleResult]]:
#     """

#     Given a line, check to see if it contains a relative markdown link.
#     The relative markdown link will look like
#     `../file.md#section_title`

#     This method will return a list of link dictionaries for each link
#     found in the line.


#     # Parameters

#     line - The text string to analyze for markdown links

#     # Return

#     A list containing RelativeMarkdownURLRuleResult objects representing each match:

#     - full-  Full text match
#     - md - The string representing the link.
#     - section -      The string representing the section anchor, if any.
#     - md_span -      A tuple(start, end) Containing the starting and ending position of the markdown link match in the string
#     - section_span - A tuple(start, end) Containing the starting and ending position of the section anchor match in the string and ending position of the section anchor match in the string

#     # Note

#     The line classifier rules perform memoization and should be
#     instantiated above the loop that calls this method. I don't expect
#     many duplicate lines so this optimization is not necessary. Mostly
#     it is about the match and the extract data

#     """

#     matches = []

#     relative_rule = RelativeMarkdownURLRule()

#     for r in extract_markdown_links(line):

#         url = r.url

#         if relative_rule.match(url):
#             # matches.append(relative_rule.extract_data(url))

#             matches.append(MarkdownLinkRuleResult(*r, relative=relative_rule.extract_data(url)))

#     return matches


# def extract_markdown_image_links(line:str) -> Optional[list[MarkdownImageRuleResult]]:
#     """

#     Given a line, return all of the markdown image links. The markdown
#     image links will be of the form:

#     ![image caption](URL).

#     Returns a list of dictionaries representing the image links.

#     # Parameters

#     line:- The text string to analyze for markdown links

#     # Return

#     A list of dictionaries keyed by:

#     - `caption` - The image caption portion of the link -> ![image caption](URL)
#     - `image` - The url to the image

#     """

#     image_rule = MarkdownImageRule()

#     # Contains a valid markdown link?
#     if image_rule.match(line.strip()):

#         return image_rule.extract_data(line.strip())

#     return []


# def extract_markdown_image_links(line: str) -> Optional[list[MarkdownLinkRuleResult]]:
#     """

#     Given a line, return all of the markdown image links that are
#     relative links. The markdown image links will be of the form:

#     ![image caption](URL).

#     Returns a list of dictionaries representing the relative image
#     links.

#     # Parameters

#     line:str
#         - The text string to analyze for markdown links

#     # Return

#     A list of dictionaries keyed by:

#     - `caption` - The image caption portion of the link -> !
#       [image caption](URL)
#     - `url` - The url to the image

#     """

#     image_rule = MarkdownImageRule()
#     relative_rule = RelativeMarkdownURLRule()

#     matches = []

#     if image_rule.match(line.strip()):

#         for r in image_rule.extract_data(line.strip()):

#             link = MarkdownLinkRuleResult(
#                 full=r.full,
#                 text=r.text,
#                 url=r.url,
#             )

#             if relative_rule.match(link.url):

#                 link = MarkdownLinkRuleResult(
#                     full=link.full,
#                     text=link.text,
#                     url=link.url,
#                     relative=relative_rule.extract_data(link.url),
#                 )

#             matches.append(link)

#     return matches


# def adjust_markdown_links(line, md_file, **kwargs):
#     """

#     Given the line, find all markdown links that are relative links.

#     If a markdown link is detected within the line, we can do a couple
#     of things to it. It will check for intra-document links
#     (relative links) and:

#     1. Remove them, leaving a link to a section anchor
#     2. Rename the .md file to .html leaving the links intact

#     A markdown link is of the form: [text](URL)

#     1. Does the line contain a markdown link?
#     2. Is the URL portion absolute (http://www.iring.ca)?
#     3. Is the URL relative (../file.md#section_title)?

#     - If it is not a markdown link the line is returned unaltered.
#     - If the URL is absolute, the line is returned unaltered.

#     Option 1:

#     - If the URL is relative, the markdown file is removed
#     - if the URL is relative and doesn't contain a section id an
#       exception is raised.
#         - The user obviously wants to link to the beginning of the
#           document. This should be allowed for the cases where the
#           individual markdown will be compiled to standalone HTML.
#           However, since this is a compressed/merged format this
#           doesn't make sense. We could read the document and figure it
#           out, but we don't want to. It should be explicit if we are
#           compressing/merging the document into one compressed format.

#     Option 2:

#     - If the URL is relative, the markdown file is renamed to .html.


#     # Parameters

#     line:str
#         - The text string to analyze for markdown links

#     md_file:pathlib.Path
#         - The full path to the markdown file that the line is from.
#         - This is used for exceptions so we know the file and line
#           number the exception occurred on.

#     # Parameters (kwargs)

#     remove_relative_md_link:bool
#         - For each relative markdown link discovered, it will remove the
#           relative path keeping a link to the section anchor
#         - Default - False

#     replace_md_extension:bool
#         - For each relative markdown link discovered, it will change the
#           markdown extension to HTML
#         - Default - False

#     # Return

#     The line object with modifications to any markdown links as
#     required.

#     # Note

#     The line classifier rules perform memoization and should be
#     instantiated above the loop that calls this method. I don't expect
#     many duplicate lines so this optimization is not necessary. Mostly
#     it is about the match and the extract data
#     """

#     remove_relative_md_link = (
#         kwargs["remove_relative_md_link"]
#         if "remove_relative_md_link" in kwargs
#         else False
#     )
#     replace_md_extension = (
#         kwargs["replace_md_extension"] if "replace_md_extension" in kwargs else False
#     )

#     if not remove_relative_md_link and not replace_md_extension:
#         console.print(
#             f"remove_relative_md_link = {remove_relative_md_link} and replace_md_extension = {replace_md_extension} - skipping link check (At least one needs to be set)."
#         )
#         return line

#     matches = extract_relative_markdown_links(line)

#     for relative_link in matches:

#         if relative_link["md"]:
#             # we have a relative path to the markdown file

#             if remove_relative_md_link:

#                 # if there is no section name, this is a problem. They will have to specify the section to link too
#                 if relative_link["section"] is None:
#                     raise ValueError(
#                         f'ERROR - Missing Section Link - {md_file.name} - "{line}" <- contains a relative link to a markdown file without a section reference "#section_name". A section id needs to be present!'
#                     )

#                 console.print(f'Removing relative file name from: "{line}"  ')
#                 line = line.replace(relative_link["md"], "")

#             if replace_md_extension:

#                 console.print(f'Replacing .md extension with .html: "{line}"  ')
#                 line = line.replace(".md", ".html")

#     return line


# def clean_atx_header_text(text):
#     """
#     The text of the ATX header can contain links and attributes that
#     should be removed before display the text.

#     # Parameters

#     text:str
#         - the text associated with the ATX header.

#     # Return

#     The cleaned text
#     """

#     md_link_rule = MarkdownLinkRule()
#     md_attribute_syntax_rule = MarkdownAttributeSyntax()

#     # Remove attributes from the text, if any
#     if md_attribute_syntax_rule.match(text):

#         for r in md_attribute_syntax_rule.extract_data(text):

#             text = text.replace(r["full"], "")

#         text = text.strip()

#     # remove markdown links, replacing them with text
#     if md_link_rule.match(text):

#         for r in md_link_rule.extract_data(text):

#             text = text.replace(r["full"], r["text"])

#         text = text.strip()

#     return text


# def extract_all_markdown_links(contents: list[str], **kwargs) -> tuple:
#     """
#     Given a list of strings representing the contents of a markdown
#     file, return a tuple containing:
#     - all links
#     - all absolute links
#     - all relative links
#     - all image links

#     # Parameters

#     contents:list(str)
#         - The list of strings representing the contents of a markdown
#           file.

#     # Parameters (kwargs)


#     # Return

#     a tuple containing four lists:

#     - all_links
#     - absolute_links
#     - relative_links
#     - image_links

#     each of these is a list of tuples:

#     - line number (0 based)
#     - dict
#         - 'full' - The full regex match - [text](link)
#         - 'text' - The text portion of the markdown link
#         - 'link' - The URL portion of the markdown link

#     relative_links:
#     - line number (0 based)
#     - dict
#         - 'full' - The full regex match - [text](link)
#         - 'text' - The text portion of the markdown link
#         - 'link' - The URL portion of the markdown link (This can and
#            will include section anchors notation)
#         - "md_span": result.span("md"),  # tuple(start, end) <- start
#            and end position of the match
#         - "md": result.group("md"),
#         - "section_span": result.span("section"),
#         - "section": section attribute i.e ../file.md#id <- the id
#            portion

#     image_links:
#     - line number (0 based)
#     - dict
#         - 'full' - The full regex match - [text](link)
#         - 'caption' - The image caption portion of the link ->
#            ![image caption](URL)
#         - 'image' - The url to the image

#     """

#     md_link_rule = MarkdownLinkRule()
#     absolute_url_rule = AbsoluteURLRule()
#     relative_url_rule = RelativeMarkdownURLRule()

#     all_links = []
#     absolute_links = []
#     relative_links = []
#     image_links = []

#     for i, line in markdown_outside_fence(contents):

#         # Contains a valid markdown link?
#         if md_link_rule.match(line.strip()):

#             results = md_link_rule.extract_data(line.strip())

#             # can be multiple links in the line...
#             for r in results:

#                 all_links.append((i, r))

#                 url = r["url"]

#                 # Is absolute url?
#                 if absolute_url_rule.match(url):

#                     absolute_links.append((i, r))

#                 # Is relative URL?
#                 elif relative_url_rule.match(url):

#                     result = relative_url_rule.extract_data(url)

#                     # Result available keys
#                     # - full - Full match
#                     # - md_span - tuple - start and end position of the
#                     #   match
#                     # - md -       the markdown url,
#                     # - section_span -  tuple - start and end position
#                     #   of attribute anchor,
#                     # - section -  attribute anchor text,

#                     r["md_span"] = result["md_span"]
#                     r["md"] = result["md"]
#                     r["section_span"] = result["section_span"]
#                     r["section"] = result["section"]

#                     relative_links.append((i, r))

#         matches = extract_markdown_image_links(line)

#         if matches:

#             for m in matches:
#                 image_links.append((i, m))

#     return all_links, absolute_links, relative_links, image_links


# def markdown_outside_fence(
#     contents: list[str],
# ) -> Generator[tuple[int, str], None, None]:
#     """
#     A generator which iterates the entire `contents` of the Markdown
#     file line-by-line. It yields each line along with its index within
#     the list.

#     It ignores lines that are part of YAML block or a code fence.

#     # Parameters

#     contents - the lines of the markdown file.

#     # Return

#     A tuple:

#     (12, "Some text on a line in the Markdown file.")

#     # NOTE

#     The index is 0 based and maps directly to the `contents` list.

#     """

#     if contents is None:
#         return  # this is effectively raising a StopIteration

#     ignore_block = MDFence()

#     for i, line in enumerate(contents):

#         if ignore_block.in_block(line):
#             continue

#         yield i, line


# @dataclass(frozen=True)
# class MarkdownDocument:
#     """ """

#     filename: Path = None

#     @cached_property
#     def contents(self) -> list[str]:
#         """
#         Return a list representing the contents of the markdown file.
#         Using indexing you can drill down by line numbers.
#         """

#         return self.filename.read_text().splitlines()

#         # with self.filename.open("r", encoding="utf-8") as fin:
#         #     return fin.readlines()

#     @cached_property
#     def line_look_up(self) -> dict[str, str]:
#         """
#         Return a dictionary keyed by a str with the value of the
#         matching line numbers.

#         Give a text string representing a line, return the list of line
#         numbers within the document that exactly match the text string.
#         essentially, it is the reverse of `self.contents`.
#         """

#         reverse = {}

#         # we could have duplicate lines, create a list of lines that
#         # match the text
#         for i, k in enumerate(self.contents):

#             reverse.setdefault(k, []).append(i)

#         return reverse

#     @cached_property
#     def links(
#         self,
#     ) -> tuple[
#         list[tuple[int, dict]],
#         list[tuple[int, dict]],
#         list[tuple[int, dict]],
#         list[tuple[int, dict]],
#     ]:
#         """
#         Extract all Markdown links:
#         - all links (absolute and relative)
#         - absolute links
#         - relative links
#         - image links - links formatted to display images

#         # Return

#         a tuple containing:

#         0. all_links
#         1. absolute_links
#         2. relative_links
#         3. image_links

#         each of these is a list of tuples:

#         - line number (0 based)
#         - dict
#             - 'full' - The full regex match - [text](link)
#             - 'text' - The text portion of the markdown link
#             - 'url' - The URL portion of the markdown link

#         relative_links:
#         - line number (0 based)
#         - dict
#             - 'full' - The full regex match - [text](link)
#             - 'text' - The text portion of the markdown link - [text](link)
#             - 'url' - The URL portion of the markdown link - [text](link) (This can and will include section anchors notation)
#             - "md_span": result.span("md"),  # tuple(start, end) <- start and end position of the match
#             - "md": result.group("md"),
#             - "section_span": result.span("section"),
#             - "section": section attribute i.e ../file.md#id <- the id portion,

#         image_links:
#         - line number (0 based)
#         - dict
#             - 'full' - The full regex match - [text](link)
#             - 'caption' - The image caption portion of the link -> ![caption](URL)
#             - 'url' - The URL to the image

#         """

#         return extract_all_markdown_links(self.contents)

#     def all_links(self):
#         return self.links[0]

#     def absolute_links(self):
#         return self.links[1]

#     def relative_links(self):
#         return self.links[2]

#     def image_links(self):
#         return self.links[3]
