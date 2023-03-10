#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams

# uuid   = 62d0f764-b927-11ed-875e-04cf4bfb0bc5
# author = Troy Williams
# email  = troy.williams@bluebill.net
# date   = 2023-03-02
# -----------

"""
Code specific to Myst Markdown Variant
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
    CodeFenceRuleResult,
    CodeFenceRule,
    YamlBlockRule,
    DirectiveStringRuleResult,
    DirectiveStringRule,
)

from .markdown import (
    LineNumber,
)

# -------------


class DirectiveFence:
    """
    This object keeps track of whether we are iterating through a code
    fence block while iterating through a
    markdown strings.

    # kwargs

    exclude_tails - bool - indicates we want to ignore the start and end
    of the block

    directive_name - Optional[str] - The name of the directive block. If
    it is None, we include all directive blocks.

    # Usage

    ```
    ignore_block = DirectiveFence()

    for line in contents:

        if ignore_block.in_block(line):
            continue

        # The line isn't part of a code fence. Process it.
    ```

    """

    def __init__(
        self,
        exclude_tails: bool = False,
        directive_name: Optional[str] = None,
        **kwargs,
    ):
        self.is_code_fence = CodeFenceRule(backticks_only=True)
        self.is_directive = DirectiveStringRule()

        self.directive_name = directive_name

        self.in_fence = False

        self.exclude_tails = exclude_tails

    def _correct_directive_name(self) -> bool:
        """ """

        if self.directive_name is None:
            return True

        return self.directive_name == self.is_directive.result.directivename

    def __call__(self, line: str = None) -> bool:
        # Are we in a block?

        if self.in_fence:
            # Are we at the end?
            if self.is_code_fence(line):
                self.in_fence = False

                if self.exclude_tails:
                    # we don't want the end markers of the block
                    return False

            # We are at the last line of the fence block, but caller
            # would consider this line still in the block. We return
            # True, but we have set the flag to false

            return True

        # Have we entered a fence block?
        if self.is_code_fence(line):
            result = self.is_code_fence.result

            if self.is_directive(result.arguments) and self._correct_directive_name():
                self.in_fence = True

                return True if not self.exclude_tails else False

        # We are not in a directive block
        return False


class YAMLFence:
    """
    This object keeps track of whether we are iterating through a YAML
    fence block while iterating through a markdown strings.


    # Usage

    ```
    ignore_block = YAMLFence()

    for line in contents:

        if ignore_block.in_block(line):
            continue

        # The line isn't part of a code fence. Process it.
    ```

    """

    def __init__(self, **kwargs):
        self.is_yaml_fence = YamlBlockRule()
        self.in_fence = False

    def __call__(self, line: str = None) -> bool:
        # Are we in a block?

        if self.in_fence:
            # Are we at the end?
            if self.is_yaml_fence(line):
                self.in_fence = False

            # We are at the last line of the fence block, but caller
            # would consider this line still in the block. We return
            # True, but we have set the flag to false

            return True

        # Have we entered a fence block?
        if self.is_yaml_fence(line):
            self.in_fence = True
            return True

        # We are not in a directive block
        return False


def inside_toctree(
    lines: Optional[Sequence[str]] = None,
    start: int = 0,
    directive_name: Optional[str] = None,
) -> Generator[LineNumber, None, None]:
    """
    This method will iterate through the lines in the sequence,
    returning the lines that are within toctree directives. It will
    ignore YAML blocks or keywords.

    # Parameters

    lines - a sequence of strings

    start - the start of the sequence to use for the line numbers.
        - Default = 0

    # Return

    A LineNumber object representing the line number and the string
    inside the toctree directive

    # Reference

    https://myst-parser.readthedocs.io/en/v0.16.1/syntax/syntax.html?highlight=directives#directives-a-block-level-extension-point

    The directive is the triple-backtics and curly brackets.

    ```

    ```{toctree}

    ```

    In general, a directive can look like this:

    ```{directivename} arguments
    ---
    key1: val1
    key2: val2
    ---
    This is
    directive content
    ```

    or

    ```{directivename} arguments
    :key1: val1
    :key2: val2

    This is
    directive content
    ```

    The toctree directive, has no arguments (we'll ignore them). But it
    can have a YAML block or keywords that will be ignored.

    """

    if lines is None:
        return  # this is effectively raising a StopIteration

    in_directive_block = DirectiveFence(
        exclude_tails=True,
        directive_name=directive_name,
    )
    in_yaml_block = YAMLFence()

    for i, line in enumerate(lines, start=start):
        if in_directive_block(line):
            # Are we in a YAML block
            if in_yaml_block(line):
                continue

            # Check for the Short Hand Variable keys
            if line.strip().startswith(":"):
                continue

            yield LineNumber(i, line)


def toctree_links(link: str, document: Path, root: Path) -> Optional[list[Path]]:
    """
    This method is designed to process lines within a `toctree` directive.
    Each line represent a link to a file within the documentation
    structure. It assumes all documentation is stored within a `root`
    folder and that we are examining the `toctree` from the `document`.
    This method will look at one `link` at a time.

    If the file exists, it will return the full path to the link
    relative to the `root`.

    It is assumed that a link refers to a file:

    - It can be referred to by an absolute or relative path

    - An absolute file starts with a / while a relative file does not

    - The absolute file is absolute from the root_path
        - root = /src/docs
        - link = /help/index.md
        - path -> /src/docs/help/index.md

    - The relative file is relative to the document it is in
        - root = /src/docs
        - link = help/index.md
        - document = test/test.md
        - path -> /src/docs/test/help/index.md

    - it supports globs, so *, index*, index/* or *.md are acceptable

    # Args

    link - A string representing the path to the file(s)

    document - The path of the document that the link is from. It should
    be relative to the `root`

    root - The full path to the documentation root folder.

    # Return

    A full Path pointing to the file in the link

    """

    if len(link) == 0:
        return None

    resolved_link = None

    if link.startswith("/"):
        # we have an absolute string, combine it with root

        resolved_link = (root / Path(*Path(link).parts[1:])).resolve()

    else:
        # we have a relative string, combine it with the document
        # parent

        resolved_link = (root / document.parent / Path(link)).resolve()

    # NOTE: calling resolve will resolve the `..` and `.` that may be in
    # the path

    # Do we have any wildcards in the path?
    if m := [i for i, p in enumerate(resolved_link.parts) if "*" in p]:
        # cover these basic cases - anything more advanced can be dealt
        # with later - we'll only deal with ONE wildcard in the path,
        # namely the asterix

        # 1. *
        # 2. index*
        # 3. *index
        # 4. test/*

        index = m.pop()
        search_path = Path(*resolved_link.parts[:index])

        return [
            f for f in search_path.glob(resolved_link.parts[index]) if f != document
        ]

    else:
        return [resolved_link]
