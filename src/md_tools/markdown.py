#!/usr/bin/env python3
#-*- coding:utf-8 -*-

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

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Generator


# ------------
# 3rd Party - From PyPI

# ------------
# Custom Modules

from .markdown_classifiers import (
    AbsoluteURLRule,
    ATXHeaderRule,
    MarkdownAttributeSyntax,
    MarkdownImageRule,
    MarkdownLinkRule,
    MDFence,
    RelativeMarkdownURLRule,
)


# -------------

# define the rules outside so they can take advantage of memoization
# (if any headers repeat - probably unlikely)

atx_rules = [
    ATXHeaderRule(key="Rule 1", count=1),
    ATXHeaderRule(key="Rule 2", count=2),
    ATXHeaderRule(key="Rule 3", count=3),
    ATXHeaderRule(key="Rule 4", count=4),
    ATXHeaderRule(key="Rule 5", count=5),
    ATXHeaderRule(key="Rule 6", count=6),
]

md_link_rule = MarkdownLinkRule()
md_attribute_syntax_rule = MarkdownAttributeSyntax()


def find_atx_header(line, **kwargs):
    """

    Determine if the line is an ATX header or not. If it is an ATX
    header it will return a tuple containing the header number (1 to 6)
    and the text of the header.

    # Parameters

    line:str
        - The string to check for an ATX header.

    # Return

    A tuple containing the heading level (1 to 6) and the string of the
    header (not the ATX header syntax).

    # Note

    We do not consider more than 6 indentation levels to be an ATX
    header.(https://spec.commonmark.org/0.24/#atx-headings).

    """

    for rule in atx_rules:

        if rule.match(line):
            return rule.atx_count, rule.extract_data(line)

    return None


def find_all_atx_headers(contents, **kwargs):
    """
    Given a list of strings representing the contents of a markdown
    file, return a list of section headers.

    # Parameters

    contents:list(str)
        - The list of strings representing the contents of a markdown
          file.

    # Parameters (kwargs)

    include_line_numbers:bool
        - Add the line number in the contents where it found the
          contents

    # Return

    A list of tuples representing the line number (0 based), header
    level (1 to 6) and the header text

    (23, 2, "Level 2 header {#AnchorName}    ")

    """

    include_line_numbers = (
        kwargs["include_line_numbers"] if "include_line_numbers" in kwargs else False
    )

    headers = []

    for i, line in markdown_outside_fence(contents):

        result = find_atx_header(line)

        if result:
            if include_line_numbers:
                result = (i, *result)

            headers.append(result)

    return headers


def section_to_anchor(s):
    """
    Given the text of an ATX header, construct a valid anchor from it.
    NOTE: it is expecting the text of the ATX header and not the syntax
    defining the ATX header i.e. it shouldn't contain leading #.

    From [Pandoc]
    (https://pandoc.org/MANUAL.html#extension-auto_identifiers):

    ```
    The default algorithm used to derive the identifier from the
    heading text is:

    - Remove all formatting, links, etc.
    - Remove all footnotes.
    - Remove all non-alphanumeric characters, except underscores,
      hyphens, and periods.
    - Replace all spaces and newlines with hyphens.
    - Convert all alphabetic characters to lowercase.
    - Remove everything up to the first letter (identifiers may not
      begin with a number or punctuation mark).
    - If nothing is left after this, use the identifier section.

    Thus, for example,
    Heading                         Identifier
    Heading identifiers in HTML     heading-identifiers-in-html
    Maître d'hôtel                  maître-dhôtel
    *Dogs*?--in *my* house?         dogs--in-my-house
    [HTML], [S5], or [RTF]?         html-s5-or-rtf
    3. Applications                 applications
    33                              section

    Preamble {#sec:ch0_0_preamble-1}  sec:ch0_0_preamble-1
    ```

    These anchors can be used in links:
    ```
    See the section on
    [heading identifiers](#heading-identifiers-in-html-latex-and-context).
    ```

    # NOTE

    Pandoc Extension: gfm_auto_identifiers

    Changes the algorithm used by auto_identifiers to conform to
    GitHub’s method. Spaces are converted to dashes (-), uppercase
    characters to lowercase characters, and punctuation characters
    other than - and _ are removed.

    We'll stick with the basics (for now).

    Reference:

    - https://stackoverflow.com/questions/1007481/how-do-i-replace-whitespaces-with-underscore

    Could use some slugify methods:

    - https://github.com/un33k/python-slugify

    """

    # Is there header attribute syntax?

    # https://pandoc.org/MANUAL.html#extension-fenced_code_attributes
    # 'Equations {#sec:ch0_2_equations-1}' <- handle this case
    #  with "header attribute syntax" We are looking for
    #  {#sec:ch0_2} the hashtag identifier that denotes a section name,
    #  just return this if it is found... NOTE: There should only be
    #  one match, so we return the first match

    if md_attribute_syntax_rule.match(s):
        for r in md_attribute_syntax_rule.extract_data(s):
            return r["id"]

    # Do we have markdown links?
    # [pandoc-fignos](https://github.com/tomduck/pandoc-fignos) Usage

    if md_link_rule.match(s):
        for r in md_link_rule.extract_data(s):
            s = s.replace(r["full"], r["text"])

    # Convert all alphabetic characters to lowercase and remove trailing
    # and leading spaces

    s = s.lower()

    # Replace all spaces and newlines with hyphens.

    s = re.sub(r"\s+", "-", s)

    # Remove all non-alphanumeric characters, except underscores,
    # hyphens, and periods.

    s = re.sub(r"[^\w_\-.]", "", s)

    # we could probably do more, but let's leave it here for now....

    return s


def extract_markdown_links(line, **kwargs):
    """

    Given a line, return all of the markdown links. The markdown links
    will be of the form:

    (Description)[URL]

    (This is a link)[../file.md#section_title]

    This method will return a list of link dictionaries for each link
    found in the line.

    # Parameters

    line:str
        - The text string to analyze for markdown links

    # Return

    Assume that the markdown link looks like this in the text:
    - (Description)[URL]
    - (This is a link)[../file.md#section_title]
    - [text](link)

    This method will return a list of dictionaries keyed as follows:

    A list containing dictionaries representing each match. The
    dictionary contains the following keys:

    - `full` - The full regex match - [text](link)
    - `text` - The text portion of the markdown link
    - `link` - The URL portion of the markdown link

    # Note

    The line classifier rules perform memoization and should be
    instantiated above the loop that calls this method. I don't expect
    many duplicate lines so this optimization is not necessary. Mostly
    it is about the match and the extract data

    """

    link_rule = MarkdownLinkRule()

    matches = []

    if link_rule.match(line.strip()):

        matches = link_rule.extract_data(line.strip())

    return matches


def extract_relative_markdown_links(line, **kwargs):
    """

    Given a line, check to see if it contains a relative markdown link.
    The relative markdown link will look like
    `../file.md#section_title`

    This method will return a list of link dictionaries for each link
    found in the line.


    # Parameters

    line:str
        - The text string to analyze for markdown links

    # Return

    A list containing dictionaries representing each match. The
    dictionary contains the following keys:

    - `md` -           The string representing the link.
    - `section` -      The string representing the section anchor, if
      any.
    - `md_span` -      A tuple(start, end) Containing the starting and
      ending position of the markdown link match in the string
    - `section_span` - A tuple(start, end) Containing the starting and
      ending position of the section anchor match in the string

    # Note

    The line classifier rules perform memoization and should be
    instantiated above the loop that calls this method. I don't expect
    many duplicate lines so this optimization is not necessary. Mostly
    it is about the match and the extract data

    """

    matches = []

    relative_rule = RelativeMarkdownURLRule()

    for r in extract_markdown_links(line):

        url = r["url"]

        if relative_rule.match(url):
            matches.append(relative_rule.extract_data(url))

    return matches


def extract_markdown_image_links(line, **kwargs):
    """

    Given a line, return all of the markdown image links. The markdown
    image links will be of the form:

    ![image caption](URL).

    Returns a list of dictionaries representing the image links.

    # Parameters

    line:str
        - The text string to analyze for markdown links

    # Return

    A list of dictionaries keyed by:

    - `caption` - The image caption portion of the link -> !
      [image caption](URL)
    - `image` - The url to the image

    """

    image_rule = MarkdownImageRule()

    # Contains a valid markdown link?
    if image_rule.match(line.strip()):

        return image_rule.extract_data(line.strip())

    return []


def extract_relative_markdown_image_links(line, **kwargs):
    """

    Given a line, return all of the markdown image links that are
    relative links. The markdown image links will be of the form:

    ![image caption](URL).

    Returns a list of dictionaries representing the relative image
    links.

    # Parameters

    line:str
        - The text string to analyze for markdown links

    # Return

    A list of dictionaries keyed by:

    - `caption` - The image caption portion of the link -> !
      [image caption](URL)
    - `image` - The url to the image

    """

    relative_rule = RelativeMarkdownURLRule()

    matches = []

    for m in extract_markdown_image_links(line):

        if relative_rule.match(m["url"]):

            result = relative_rule.extract_data(m["url"])

            matches.append(result | m)

    return matches


def adjust_markdown_links(line, md_file, **kwargs):
    """

    Given the line, find all markdown links that are relative links.

    If a markdown link is detected within the line, we can do a couple
    of things to it. It will check for intra-document links
    (relative links) and:

    1. Remove them, leaving a link to a section anchor
    2. Rename the .md file to .html leaving the links intact

    A markdown link is of the form: [text](URL)

    1. Does the line contain a markdown link?
    2. Is the URL portion absolute (http://www.iring.ca)?
    3. Is the URL relative (../file.md#section_title)?

    - If it is not a markdown link the line is returned unaltered.
    - If the URL is absolute, the line is returned unaltered.

    Option 1:

    - If the URL is relative, the markdown file is removed
    - if the URL is relative and doesn't contain a section id an
      exception is raised.
        - The user obviously wants to link to the beginning of the
          document. This should be allowed for the cases where the
          individual markdown will be compiled to standalone HTML.
          However, since this is a compressed/merged format this
          doesn't make sense. We could read the document and figure it
          out, but we don't want to. It should be explicit if we are
          compressing/merging the document into one compressed format.

    Option 2:

    - If the URL is relative, the markdown file is renamed to .html.


    # Parameters

    line:str
        - The text string to analyze for markdown links

    md_file:pathlib.Path
        - The full path to the markdown file that the line is from.
        - This is used for exceptions so we know the file and line
          number the exception occurred on.

    # Parameters (kwargs)

    remove_relative_md_link:bool
        - For each relative markdown link discovered, it will remove the
          relative path keeping a link to the section anchor
        - Default - False

    replace_md_extension:bool
        - For each relative markdown link discovered, it will change the
          markdown extension to HTML
        - Default - False

    # Return

    The line object with modifications to any markdown links as
    required.

    # Note

    The line classifier rules perform memoization and should be
    instantiated above the loop that calls this method. I don't expect
    many duplicate lines so this optimization is not necessary. Mostly
    it is about the match and the extract data
    """

    remove_relative_md_link = (
        kwargs["remove_relative_md_link"]
        if "remove_relative_md_link" in kwargs
        else False
    )
    replace_md_extension = (
        kwargs["replace_md_extension"] if "replace_md_extension" in kwargs else False
    )

    if not remove_relative_md_link and not replace_md_extension:
        console.print(
            f"remove_relative_md_link = {remove_relative_md_link} and replace_md_extension = {replace_md_extension} - skipping link check (At least one needs to be set)."
        )
        return line

    matches = extract_relative_markdown_links(line)

    for relative_link in matches:

        if relative_link["md"]:
            # we have a relative path to the markdown file

            if remove_relative_md_link:

                # if there is no section name, this is a problem. They will have to specify the section to link too
                if relative_link["section"] is None:
                    raise ValueError(
                        f'ERROR - Missing Section Link - {md_file.name} - "{line}" <- contains a relative link to a markdown file without a section reference "#section_name". A section id needs to be present!'
                    )

                console.print(f'Removing relative file name from: "{line}"  ')
                line = line.replace(relative_link["md"], "")

            if replace_md_extension:

                console.print(f'Replacing .md extension with .html: "{line}"  ')
                line = line.replace(".md", ".html")

    return line


def clean_atx_header_text(text):
    """
    The text of the ATX header can contain links and attributes that
    should be removed before display the text.

    # Parameters

    text:str
        - the text associated with the ATX header.

    # Return

    The cleaned text
    """

    md_link_rule = MarkdownLinkRule()
    md_attribute_syntax_rule = MarkdownAttributeSyntax()

    # Remove attributes from the text, if any
    if md_attribute_syntax_rule.match(text):

        for r in md_attribute_syntax_rule.extract_data(text):

            text = text.replace(r["full"], "")

        text = text.strip()

    # remove markdown links, replacing them with text
    if md_link_rule.match(text):

        for r in md_link_rule.extract_data(text):

            text = text.replace(r["full"], r["text"])

        text = text.strip()

    return text

def extract_all_markdown_links(contents:list[str], **kwargs) -> tuple:
    """
    Given a list of strings representing the contents of a markdown
    file, return a tuple containing:
    - all links
    - all absolute links
    - all relative links
    - all image links

    # Parameters

    contents:list(str)
        - The list of strings representing the contents of a markdown
          file.

    # Parameters (kwargs)


    # Return

    a tuple containing four lists:

    - all_links
    - absolute_links
    - relative_links
    - image_links

    each of these is a list of tuples:

    - line number (0 based)
    - dict
        - 'full' - The full regex match - [text](link)
        - 'text' - The text portion of the markdown link
        - 'link' - The URL portion of the markdown link

    relative_links:
    - line number (0 based)
    - dict
        - 'full' - The full regex match - [text](link)
        - 'text' - The text portion of the markdown link
        - 'link' - The URL portion of the markdown link (This can and
           will include section anchors notation)
        - "md_span": result.span("md"),  # tuple(start, end) <- start
           and end position of the match
        - "md": result.group("md"),
        - "section_span": result.span("section"),
        - "section": section attribute i.e ../file.md#id <- the id
           portion

    image_links:
    - line number (0 based)
    - dict
        - 'full' - The full regex match - [text](link)
        - 'caption' - The image caption portion of the link ->
           ![image caption](URL)
        - 'image' - The url to the image

    """

    md_link_rule = MarkdownLinkRule()
    absolute_url_rule = AbsoluteURLRule()
    relative_url_rule = RelativeMarkdownURLRule()

    all_links = []
    absolute_links = []
    relative_links = []
    image_links = []

    for i, line in markdown_outside_fence(contents):

        # Contains a valid markdown link?
        if md_link_rule.match(line.strip()):

            results = md_link_rule.extract_data(line.strip())

            # can be multiple links in the line...
            for r in results:

                all_links.append((i, r))

                url = r["url"]

                # Is absolute url?
                if absolute_url_rule.match(url):

                    absolute_links.append((i, r))

                # Is relative URL?
                elif relative_url_rule.match(url):

                    result = relative_url_rule.extract_data(url)

                    # Result available keys
                    # - full - Full match
                    # - md_span - tuple - start and end position of the
                    #   match
                    # - md -       the markdown url,
                    # - section_span -  tuple - start and end position
                    #   of attribute anchor,
                    # - section -  attribute anchor text,

                    r["md_span"] = result["md_span"]
                    r["md"] = result["md"]
                    r["section_span"] = result["section_span"]
                    r["section"] = result["section"]

                    relative_links.append((i, r))

        matches = extract_markdown_image_links(line)

        if matches:

            for m in matches:
                image_links.append((i, m))

    return all_links, absolute_links, relative_links, image_links


def markdown_outside_fence(contents:list[str]) -> Generator[tuple[int, str], None, None]:
    """
    A generator which iterates the entire `contents` of the Markdown
    file line-by-line. It yields each line along with its index within
    the list.

    It ignores lines that are part of YAML block or a code fence.

    # Parameters

    contents - the lines of the markdown file.

    # Return

    A tuple:

    (12, "Some text on a line in the Markdown file.")

    # NOTE

    The index is 0 based and maps directly to the `contents` list.

    """

    if contents is None:
        return # this is effectively raising a StopIteration

    ignore_block = MDFence()

    for i, line in enumerate(contents):

        if ignore_block.in_block(line):
            continue

        yield i, line




@dataclass(frozen=True)
class MarkdownDocument():
    """
    """

    filename: Path = None

    @cached_property
    def contents(self) -> list[str]:
        """
        Return a list representing the contents of the markdown file.
        Using indexing you can drill down by line numbers.
        """

        return self.filename.read_text().splitlines()

        # with self.filename.open("r", encoding="utf-8") as fin:
        #     return fin.readlines()


    @cached_property
    def line_look_up(self) -> dict[str,str]:
        """
        Return a dictionary keyed by a str with the value of the
        matching line numbers.

        Give a text string representing a line, return the list of line
        numbers within the document that exactly match the text string.
        essentially, it is the reverse of `self.contents`.
        """

        reverse = {}

        # we could have duplicate lines, create a list of lines that
        # match the text
        for i, k in enumerate(self.contents):

            reverse.setdefault(k, []).append(i)

        return reverse

    @cached_property
    def links(self) -> tuple[list[tuple[int, dict]], list[tuple[int, dict]], list[tuple[int, dict]], list[tuple[int, dict]],]:
        """
        Extract all Markdown links:
        - all links (absolute and relative)
        - absolute links
        - relative links
        - image links - links formatted to display images

        # Return

        a tuple containing:

        0. all_links
        1. absolute_links
        2. relative_links
        3. image_links

        each of these is a list of tuples:

        - line number (0 based)
        - dict
            - 'full' - The full regex match - [text](link)
            - 'text' - The text portion of the markdown link
            - 'url' - The URL portion of the markdown link

        relative_links:
        - line number (0 based)
        - dict
            - 'full' - The full regex match - [text](link)
            - 'text' - The text portion of the markdown link - [text](link)
            - 'url' - The URL portion of the markdown link - [text](link) (This can and will include section anchors notation)
            - "md_span": result.span("md"),  # tuple(start, end) <- start and end position of the match
            - "md": result.group("md"),
            - "section_span": result.span("section"),
            - "section": section attribute i.e ../file.md#id <- the id portion,

        image_links:
        - line number (0 based)
        - dict
            - 'full' - The full regex match - [text](link)
            - 'caption' - The image caption portion of the link -> ![caption](URL)
            - 'url' - The URL to the image

        """

        return extract_all_markdown_links(self.contents)

    def all_links(self):
        return self.links[0]

    def absolute_links(self):
        return self.links[1]

    def relative_links(self):
        return self.links[2]

    def image_links(self):
        return self.links[3]
