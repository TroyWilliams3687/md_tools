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

from collections.abc import Sequence, Generator, Callable
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

        self.in_fence = dict(zip(self.fence_types, (False, False)))

    def __call__(self, line: str = None) -> bool:
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

    number: int
    line: str


def outside_fence(
    lines: Optional[Sequence[str]] = None, start: int = 0
) -> Generator[LineNumber, None, None]:
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
    matches - a sequence of matches within the line
    """

    number: int
    line: str
    matches: Optional[Sequence]


def _rule_filter(
    rules: Sequence[Callable],
    lines: Optional[Sequence[str]] = None,
    start: int = 0,
) -> Generator[LinkLineNumber, None, None]:
    """
    A method that applies a rule to filter the results of iterating
    through the outside_fence method.
    """

    for valid_line in outside_fence(lines, start=start):
        matches = []
        for rule in rules:
            if rule(valid_line.line):
                matches += rule.result

        if matches:
            yield LinkLineNumber(*valid_line, matches=matches)


def markdown_links(
    lines: Optional[Sequence[str]] = None,
    start: int = 0,
) -> Generator[LinkLineNumber, None, None]:
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

    yield from _rule_filter(
        rules=(MarkdownLinkRule(),),
        lines=lines,
        start=start,
    )


def markdown_relative_links(
    lines: Optional[Sequence[str]] = None,
    start: int = 0,
) -> Generator[LinkLineNumber, None, None]:
    """
    This method will return lines that contain markdown links that are
    relative.

    # Parameters

    lines - a sequence of strings

    start - the start of the sequence to use for the line numbers.
        - Default = 0

    # Return

    A LinkLineNumber object representing the line number and the string
    that contains markdown links as well as the actual matches.

    """

    all_link_rules = (MarkdownLinkRule(),)

    is_relative = RelativeURLRule()

    for line in _rule_filter(rules=all_link_rules, lines=lines, start=start):
        relative_matches = [match for match in line.matches if is_relative(match.url)]

        if relative_matches:
            yield LinkLineNumber(
                number=line.number,
                line=line.line,
                matches=relative_matches,
            )


def markdown_image_links(
    lines: Optional[Sequence[str]] = None,
    start: int = 0,
) -> Generator[LinkLineNumber, None, None]:
    """
    This method will return lines that contain markdown image links.

    # Parameters

    lines - a sequence of strings

    start - the start of the sequence to use for the line numbers.
        - Default = 0

    # Return

    A LinkLineNumber object representing the line number and the string
    that contains markdown links as well as the actual matches.

    """

    yield from _rule_filter(
        rules=(MarkdownImageLinkRule(),),
        lines=lines,
        start=start,
    )


def markdown_all_links(
    lines: Optional[Sequence[str]] = None,
    start: int = 0,
) -> Generator[LinkLineNumber, None, None]:
    """
    This method will return lines that contain markdown links and image
    links, booth relative and absolute links.

    # Parameters

    lines - a sequence of strings

    start - the start of the sequence to use for the line numbers.
        - Default = 0

    # Return

    A LinkLineNumber object representing the line number and the string
    that contains markdown links as well as the actual matches.

    """

    yield from _rule_filter(
        rules=(MarkdownLinkRule(), MarkdownImageLinkRule()),
        lines=lines,
        start=start,
    )


def markdown_all_relative_links(
    lines: Optional[Sequence[str]] = None,
    start: int = 0,
) -> Generator[LinkLineNumber, None, None]:
    """
    This method will return lines that contain markdown links and image
    links that are relative.

    # Parameters

    lines - a sequence of strings

    start - the start of the sequence to use for the line numbers.
        - Default = 0

    # Return

    A LinkLineNumber object representing the line number and the string
    that contains markdown links as well as the actual matches.

    """

    all_link_rules = (MarkdownLinkRule(), MarkdownImageLinkRule())

    is_relative = RelativeURLRule()

    for line in _rule_filter(rules=all_link_rules, lines=lines, start=start):
        relative_matches = [match for match in line.matches if is_relative(match.url)]

        if relative_matches:
            yield LinkLineNumber(
                number=line.number,
                line=line.line,
                matches=relative_matches,
            )


@dataclass(frozen=True)
class MarkdownDocument:
    """ """

    filename: Path = None

    @cached_property
    def contents(self) -> list[str]:
        """
        Return a list representing the contents of the markdown file.
        Using indexing you can drill down by line numbers.
        """

        return self.filename.read_text(encoding="utf-8").splitlines()

        # with self.filename.open("r", encoding="utf-8") as fin:
        #     return fin.readlines()

    @cached_property
    def _line_lookup(self) -> dict[str, list[int]]:
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

    def line_lookup(self, line) -> Optional[Sequence[int]]:
        """
        Given a str representing a line, what is its line number?

        If the string doesn't existing in the file, None is returned.
        """

        if line in self._line_lookup:
            return self._line_lookup[line]

        else:
            return None

    @cached_property
    def links(self) -> Optional[Sequence[LinkLineNumber]]:
        """
        A Sequence of all lines that contain Markdown hyperlinks.
        """

        return list(markdown_links(self.contents))

    @cached_property
    def relative_links(self) -> Optional[Sequence[LinkLineNumber]]:
        """
        A Sequence of all lines that contain Markdown relative hyperlinks.
        """

        return list(markdown_relative_links(self.contents))

    @cached_property
    def image_links(self) -> Optional[Sequence[LinkLineNumber]]:
        """
        A Sequence of all lines that contain Markdown image links.
        """

        return list(markdown_image_links(self.contents))

    @cached_property
    def all_links(self) -> Optional[Sequence[LinkLineNumber]]:
        """
        A Sequence of all lines that contain Markdown hyperlinks or
        Markdown image links.
        """

        return list(markdown_all_links(self.contents))

    @cached_property
    def all_relative_links(self) -> Optional[Sequence[LinkLineNumber]]:
        """
        A Sequence of all lines that contain Markdown hyperlinks or
        Markdown image links. These are filtered so only relative links
        are in the Sequence.
        """

        return list(markdown_all_relative_links(self.contents))


class ValidationIssue(NamedTuple):
    """
    A simple result from the validate_markdown_relative_links that
    encapsulates the line and the issue.
    """

    line: LinkLineNumber
    issue: Path


def validate_markdown_relative_links(
    doc: MarkdownDocument,
    assets: dict[str, Path],
) -> dict:
    """
    Validate all the relative links within the markdown document by
    comparing the files against the assets dictionary.

    doc - the markdown document to analyze
    assets - the dictionary that maps the file name with the discovered locations

    # Return

    A dict with the following keys:

    - line_count - The number of lines in the file

    - missing - A list of lines containing missing entries. That is
      entries that do not exist in the asset dictionary

    - incorrect - A list of lines containing links that have the name
      within the asset dictionary but does not match any of the paths

    """

    results: dict = {"line_count": len(doc.contents)}

    for rl in doc.all_relative_links:
        for link in rl.matches:
            match_path = Path(link.url)

            if match_path.name in assets:
                for asset in assets[match_path.name]:
                    potential_target = asset

                    if match_path == potential_target:
                        break  # found a match

                else:
                    # now matches - we know the file name exists, but is
                    # pointing to the wrong one

                    results.setdefault("incorrect", []).append(
                        ValidationIssue(
                            line=rl,
                            issue=match_path,
                        )
                    )

            else:
                # the file doesn't exist and there are no assets that match it.
                results.setdefault("missing", []).append(
                    ValidationIssue(
                        line=rl,
                        issue=match_path,
                    )
                )

    return results


def document_word_count(doc: MarkdownDocument) -> int:
    """
    Given a markdown document provide an estimate of the word count.
    """

    searcher = re.compile(r"\w+")
    return sum([len(searcher.findall(line)) for line in doc.contents])


class CountResult(NamedTuple):
    """
    The result of counting all the words in a sequence of documents
    """

    estimated_word_count: int
    estimated_page_count: float


def count_all_words(documents: Sequence[MarkdownDocument]) -> CountResult:
    """
    Given a sequence of documents, return the estimated total word count
    and the estimated number of pages.

    NOTE: 500 words is an average, see:
    https://howardcc.libanswers.com/faq/69833

    """

    if not documents:
        return CountResult(
            estimated_word_count=0,
            estimated_page_count=0.0,
        )

    # estimate the word count for each document
    word_counts = [document_word_count(doc) for doc in documents]

    # estimate the totals words
    estimated_total_words = sum(word_counts)

    estimated_pages = estimated_total_words / 500

    return CountResult(
        estimated_word_count=estimated_total_words,
        estimated_page_count=estimated_pages,
    )


def find_markdown_files(root_path: Path) -> set[MarkdownDocument]:
    """
    Search the root path and find all markdown files.

    returns a set of MarkdownDocument objects stored in a set.

    """

    # Store a reference to the Markdown files
    markdown_files: set[MarkdownDocument] = set()

    for filename in root_path.rglob("*"):
        if filename.suffix == ".md":
            markdown_files.add(MarkdownDocument(filename))

    return markdown_files


def find_all_files(root_path: Path) -> dict:
    """
    Search the root path and find all files returning a dictionary keyed
    by filename pointing at a list containing Path objects. It is
    possible to have the same filename on different paths

    NOTE: The Path objects will have the path relative to the root_path.
    """

    # ----
    # All files are considered assets, including the markdown files. The
    # assets are simply things that can be the target of a link. The
    # key will be the filename and the target a list of Path objects
    # representing files with the same name, but in different paths.

    # NOTE: When using the stored paths, they need to be relative to the
    # root folder

    assets: dict[str, Path] = {}

    for filename in root_path.rglob("*"):
        # add the asset to the correct folder, making sure it is relative to the root folder
        assets.setdefault(filename.name, []).append(Path("/") / filename.relative_to(root_path))

    return assets


def reverse_relative_links(
    md_files: Sequence[MarkdownDocument], root: Path = None
) -> dict:
    """

    Given a sequence of MarkdownDocument objects, construct a dictionary
    keyed by the filename of the document storing the list of relative
    links within the document.

    # Return

    a dictionary

    """

    md_link_lookup = {}

    for md in md_files:
        key = md.filename

        if root:
            key = key.relative_to(root)

        for ll in md.relative_links:
            for match in ll.matches:
                md_link_lookup.setdefault(key, set()).add(match.url)

    return md_link_lookup
