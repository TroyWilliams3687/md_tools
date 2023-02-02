#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams

# uuid  : 740a4b68-9837-11ed-962f-04cf4bfb0bc5
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2023-01-19
# -----------

"""
`stats` provides a pretty accurate word count using a PANDOC LUA script
and the AST representation.
"""

# ------------
# System Modules - Included with Python

from datetime import datetime
from multiprocessing import Pool
from functools import partial

# ------------
# 3rd Party - From pip

import click

from rich.console import Console

console = Console()

# ------------
# Custom Modules

# from ..documentos.common import run_cmd

# -------------


# This is the pandoc filter will will write out to a temporary location

# lua_filter = {
#     "name": "wordcount.lua",
#     "contents": [
#         "-- counts words in a document",
#         "",
#         "words = 0",
#         "",
#         "wordcount = {",
#         "  Str = function(el)",
#         "    -- we don't count a word if it's entirely punctuation:",
#         '    if el.text:match("%P") then',
#         "        words = words + 1",
#         "    end",
#         "  end,",
#         "",
#         "  Code = function(el)",
#         '    _,n = el.text:gsub("%S+","")',
#         "    words = words + n",
#         "  end,",
#         "",
#         "  CodeBlock = function(el)",
#         '    _,n = el.text:gsub("%S+","")',
#         "    words = words + n",
#         "  end",
#         "}",
#         "",
#         "function Pandoc(el)",
#         "    -- skip metadata, just count body:",
#         "    pandoc.walk_block(pandoc.Div(el.blocks), wordcount)",
#         '    print(words .. " words in body")',
#         "    os.exit(0)",
#         "end",
#     ],
# }


# def construct_pandoc_command(
#     input_file=None,
#     lua_filter=None,
# ):
#     """
#     Construct the Pandoc command.

#     # Parameters

#     input_file:pathlib.Path
#         - The file that we want to apply the lua filter too.

#     lua_filter:pathlib.Path
#         - The path to the lua filter to use for the word counts.

#     # Return

#     A list of CLI elements that will be used by subprocess.
#     """

#     # --------
#     # Basic Commands

#     return [
#         "pandoc",
#         "--lua-filter",
#         lua_filter,
#         input_file,
#     ]


# def process_markdown(
#     md=None,
#     lua_script=None,
# ):
#     """ """

#     pandoc = construct_pandoc_command(
#         input_file=md,
#         lua_filter=lua_script,
#     )

#     stdout = run_cmd(pandoc)

#     if len(stdout) == 1:

#         # The string will be of the form 'xxx words in body'. We need to
#         # strip the text and process the count
#         count = int(stdout[0].replace(" words in body", ""))

#         console.print(f"Counted {md.name} -> {count} words...")

#         return count

#     else:
#         # something is wrong
#         raise ValueError(
#             f"Unexpected Return from Pandoc. Expected 1 line, got {len(stdout)}..."
#         )


# @click.command("stats")
# @click.pass_context
# def stats(*args, **kwargs):
#     """
#     \b
#     Given the `search` path, recursively find all the Markdown files and
#     perform a word count return the stats.

#     ```
#     Started  - 2021-05-19 13:57:30.698969
#     Finished - 2021-05-19 13:57:49.755689
#     Elapsed:   0:00:19.056720

#     Total Documents:      735
#     Total Words:      182,584
#     Estimated Pages:    365.2
#     ```

#     # Usage

#     $ docs --config=./en/config.common.yaml stats

#     """

#     # Extract the configuration file from the click context
#     config = args[0].obj["cfg"]

#     # construct the lua script

#     config["cache_folder"].mkdir(parents=True, exist_ok=True)

#     lua_script = config["cache_folder"].joinpath(lua_filter["name"])

#     lua_script.write_text("\n".join(lua_filter["contents"]))

#     build_start_time = datetime.now()

#     word_counts = []

#     # We define our main processing function using keyword arguments. If
#     # we wanted to use positional arguments we would have to adjust the
#     # parameter list so that the markdown file is last. It seems like
#     # using kwargs is easier.
#     fp = partial(process_markdown, lua_script=lua_script)

#     # -----------
#     # Multi-Processing

#     # https://docs.python.org/3/library/multiprocessing.html

#     # Use max cores - default
#     with Pool(processes=None) as p:
#         word_counts = p.map(fp, config["documents.path"].rglob("*.md"))

#     # NOTE: The above works because the kwarg in fp, md is in the first
#     # position. It could have been defined using positional arguments
#     # and have the file be the second item in the list.

#     # -----------
#     build_end_time = datetime.now()

#     console.print("")
#     console.print("-----")
#     console.print(f"Started  - {build_start_time}")
#     console.print(f"Finished - {build_end_time}")
#     console.print(f"Elapsed:   {build_end_time - build_start_time}")

#     console.print("")

#     total_words = sum(word_counts)
#     words_per_page = total_words / 500

#     # 500 words is an average, see:
#     # https://howardcc.libanswers.com/faq/69833

#     console.print(f"Total Documents: {len(word_counts):>8,}")
#     console.print(f"Total Words:     {total_words:>8,}")
#     console.print(f"Estimated Pages: {words_per_page:>8,.1f}")
