#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams

# uuid  : 7872a312-9837-11ed-9b77-04cf4bfb0bc5
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2023-01-19
# -----------

"""
The `validate` command is used to analyze the Markdown files in the
system for issues. The `repair` command can fix some of the issues.
"""

# ------------
# System Modules - Included with Python

# from datetime import datetime
# from multiprocessing import Pool
# from functools import partial

from pathlib import Path
from itertools import chain

# ------------
# 3rd Party - From pip

import click

from rich.console import Console
console = Console()

# ------------
# Custom Modules

from .markdown import MarkdownDocument


# from ..documentos.document_validation import (
#     validate_urls,
#     validate_images,
# )

# -------------


@click.command("validate")
@click.pass_context
@click.argument(
    "root_path",
    type=click.Path(
        exists=True,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
)
def validate(*args, **kwargs):
    """
    Perform validation checks for Markdown files and LST files.

    # Usage

    $ docs validate ./doc/root

    $ docs validate /home/troy/repositories/documentation/aegis.documentation.sphinx/docs/source

    """
    # config = args[0].obj["cfg"]

    # ------------
    # Build code that uses pathlib.path.rglob to recursively find all markdown files

    # inspect each file, line-by-line validating:
    # Image Check - Internal
    #   - Does the file exist at the URL?
    #   - Relative Image Check
    #   - Absolute Image Check
    # File Check
    #   - Does the local file exist?
    #   - Relative
    #   - Absolute
    # URL Check
    #   - Is the URL Valid and does it point to a valid Resource?
    #   - this can use aiohttp, a queue and asyncio to speed this up

    # should build a set of rules that can be run against each line of the markdown file
    # should be able to deal gracefully with code blocks or other blocks, i.e. YAML blocks

    # perhaps use my markdown object - it might be easier. The key is to write the file line number

    ctx = args[0]

    filepath = kwargs['root_path'].expanduser().resolve()

    console.print(f'Searching: {filepath}')

    if filepath.is_file():
        console.print('[red]Root path has to be a directory.[/red]')
        ctx.abort()

    # Store a reference to the Markdown files
    markdown_files = set()

    # ----
    # All files are considered assets, including the markdown files. The
    # assets are simply things that can be the target of a link. The
    # key will be the filename and the target a list of Path objects
    # representing files with the same name, but in different paths.

    # NOTE: When using the stored paths, they need to be relative to the
    # root folder

    asset_files = {}


    for filename in filepath.rglob("*"):

        # console.print(f'[cyan]{filename}[/cyan]')
        asset_files.setdefault(filename.name, [] ).append(filename)

        if filename.suffix == '.md':

            doc = MarkdownDocument(filename)
            markdown_files.add(doc)

            console.print(f'[green]MARKDOWN: {doc.filename}[/green] -> Lines: {len(doc.contents)}')

            for l in chain(doc.relative_links(), doc.image_links()):
                line_number, value = l
                console.print(f'\tLine: {line_number} -> {value}')


            console.print()

            # console.print(f'\tLinks (Abs + Rel): {len(doc.all_links())}')
            # console.print(f'\tAbsolute: {len(doc.absolute_links())}')
            # console.print(f'\tRelative: {len(doc.relative_links())}')
            # console.print(f'\tImage:    {len(doc.image_links())}')





    # Convert the dict counts to strings and find the length so we can
    # use the value to format the numbers to line up properly f'{value:
    # {width}.{precision}}' Since this is for formatting and display, I
    # am not bothering with anything fancier

    width = max(len(str(len(markdown_files))), len(str(len(asset_files))))

    console.print('Discovered:')
    console.print(f'Markdown files: {len(markdown_files):>{width}}')
    console.print(f'All files:      {len(asset_files):>{width}}')









# def multiprocessing_wrapper(root, md):
#     """
#     Simple wrapper to make multiprocessing easier.

#     Returns a tuple containing the file name/key and the defects or it
#     returns None.

#     NOTE: This methods arguments are defined this way to make use of
#     functools.partial

#     """

#     url_messages = validate_urls(md, root=root)
#     p = md.filename.relative_to(root)

#     if url_messages:
#         console.print("")
#         console.print(f"URL Issues in `{p}`:")

#         for msg in url_messages:
#             console.print(f"\t{msg}")

#     image_messages = validate_images(md, root=root)

#     if image_messages:
#         console.print("")
#         console.print(f"Image Issues in `{p}`:")

#         for msg in image_messages:
#             console.print(f"\t{msg}")

#     if not md.yaml_block:
#         console.print("")
#         console.print(f"Missing YAML Block: `{p}`:")

#     elif "UUID" not in md.yaml_block:
#         console.print("")
#         console.print(f"Missing UUID in YAML Block: `{p}`:")

#     elif len(md.yaml_block["UUID"]) == 0:
#         console.print("")
#         console.print(f"Empty UUID in YAML Block: `{p}`:")

#     return md


# @validate.command("markdown")
# @click.pass_context
# def markdown(*args, **kwargs):
#     """
#     \b
#     Validate the Markdown files in the system looking for URL issues.

#     # Usage

#     $ docs validate markdown

#     """

#     # Extract the configuration file from the click context
#     config = args[0].obj["cfg"]

#     build_start_time = datetime.now()

#     # ------
#     # Validate Markdown Files

#     # - absolute URL check
#     # - relative URL check
#     # - image URL check

#     console.print("Validating Markdown Files...")
#     console.print("")

#     # -----------
#     # Multi-Processing

#     # Pre-fill the bits that don't change during iteration so we can use
#     # the multiprocessing pool effectively

#     fp = partial(multiprocessing_wrapper, config["documents.path"])

#     with Pool(processes=None) as p:
#         md_files = p.map(fp, config["md_file_contents"])

#     # check for duplicate UUID values and UUID values that are not 36 characters
#     # UUID = xxxxxxxx-yyyy-zzzz-wwww-mmmmmmmmmmmm -> 36 characters

#     uuid_map = {}
#     for md in md_files:
#         if md.yaml_block and "UUID" in md.yaml_block:

#             uuid_map.setdefault(md.yaml_block["UUID"], []).append(md)

#     for uuid, files in uuid_map.items():

#         if len(uuid) != 36:
#             console.print("")

#             console.print(f"{uuid} - not 36 characters!")
#             for f in files:
#                 console.print(f"\t{f.filename}")

#             console.print("")

#         if len(files) > 1:

#             console.print("\nDuplicate UUID:")

#             for f in files:
#                 console.print(f"{f.filename}")

#             console.print("")

#     # --------------
#     build_end_time = datetime.now()

#     console.print("")
#     console.print("-----")
#     console.print(f"Started  - {build_start_time}")
#     console.print(f"Finished - {build_end_time}")
#     console.print(f"Elapsed:   {build_end_time - build_start_time}")


# @validate.command("lst")
# @click.pass_context
# def lst(*args, **kwargs):
#     """
#     \b
#     Validate the LST files in the system and ensure they all contain
#     references to valid Markdown or LST files.

#     # Usage

#     $ docs validate lst

#     """

#     # Extract the configuration file from the click context
#     config = args[0].obj["cfg"]

#     # ------
#     # Validate LST Files

#     # check for duplicate entries

#     console.print("Validating LST Files...")
#     console.print("")

#     for lst in config["lst_file_contents"]:

#         key = lst.filename.relative_to(config["documents.path"])

#         console.print(f"{key}")

#         for f in lst.links:

#             if not f.exists():
#                 console.print(f"{f} does not exist in: {key}")

#     # ------
#     # Display any files that are not included in any of the lst files

#     lst_files = {str(f) for lst in config["lst_file_contents"] for f in lst.links}
#     md_files = {str(f.filename) for f in config["md_file_contents"]}

#     console.print("Check - Are all markdown files accounted for in the LST files....")

#     console.print(f"MD Files (lst): {len(lst_files)}")
#     console.print(f"MD files (file system): {len(md_files)}")

#     # Subtracting the sets will give use the difference, that is what
#     # files are not listed in the LST file. We have to check both was
#     # because of the way the set differences work. a - b will list all
#     # the elements in a that are not in b.

#     if lst_files >= md_files:

#         delta = lst_files - md_files
#         msg = "Files that are in the LST but not in the set of MD files:"

#     else:

#         delta = md_files - lst_files
#         msg = "Files that are in the FILE SYSTEM but not in the set of LST files:"

#     if delta:

#         console.print("")
#         console.print(msg)

#         for d in delta:
#             console.print(f"\t{d}")

#         console.print("")
#         console.print(f"Count: {len(delta)}")
