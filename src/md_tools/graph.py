#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams

# uuid  : 82f548be-9837-11ed-b9e6-04cf4bfb0bc5
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2023-01-19
# -----------

"""
The graph command will display a network plot, showing the inter-connections
between all of the documents in the system.
"""

# ------------
# System Modules - Included with Python

import time

from pathlib import Path
from datetime import timedelta

# ------------
# 3rd Party - From pip

import click
import networkx as nx
import matplotlib.pyplot as plt

from rich.console import Console

console = Console()

# ------------
# Custom Modules

from .markdown import (
    MarkdownDocument,
    find_markdown_files,
    find_all_files,
    reverse_relative_links,
)

from md_tools.myst import (
    inside_toctree,
)

# -------------


def create_sub_graph(G, incoming_limit=1, outgoing_limit=0):
    """
    Given the DAG, return a sub-graph where the nodes have the incoming
    and outgoing connections.
    """

    sub_graph = nx.DiGraph()

    # find the nodes that only have one incoming edge and 0 outgoing
    for n in G.nodes:
        incoming = G.in_edges(nbunch=n)
        outgoing = G.out_edges(nbunch=n)

        if len(incoming) == incoming_limit and len(outgoing) == outgoing_limit:
            sub_graph.add_edges_from(G.in_edges(nbunch=n))

    return sub_graph


def construct_edges(md_links, root=None):
    """
    Find all links between the markdown files.
    """

    edges = []

    for md in md_links:
        key = md

        if root:
            key = key.relative_to(root)

        if key in md_links:
            for rl in md_links[key]:
                edges.append((key, str(rl)))

    return edges


@click.command("graph")
@click.pass_context
@click.argument(
    "root",
    type=click.Path(
        exists=True,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
)
@click.argument(
    "document",
    type=str,
)
def graph(*args, **kwargs):
    """
    Given the root folder and a document as the starting point,
    construct the DAG.

    Specify the root folder and the relative path to the starting document.

    NOTE: The relative path to the starting document, should be that. If the source folder is:

    /path/to/src

    and the document is

    /path/to/src/documents/index.md

    the document should be: documents/index.md

    # Usage

    $ docs graph /home/troy/repositories/documentation/aegis.documentation.sphinx/docs/source index.md

    """

    root_path = kwargs["root"].expanduser().resolve()

    console.print(f"Searching: {root_path}")

    if root_path.is_file():
        console.print("[red]Root path has to be a directory.[/red]")
        ctx.abort()

    document = Path(kwargs["document"])

    # https://stackoverflow.com/a/49667269
    # https://docs.python.org/3/library/time.html
    search_start_time = time.monotonic_ns()

    markdown_files: set[MarkdownDocument] = find_markdown_files(root_path)

    # -----------
    # Test code - should be implemented in the Markdown file itself

    md = MarkdownDocument(root_path / document)

    # console.print(md.filename)
    for line in inside_toctree(md.contents, directive_name="toctree"):
        console.print(line)

        # - If the line is not empty, assume it points to a file
        # - The file can be absolute or relative
        # - an absolute file starts with a / while a relative file does not
        # - The absolute file is absolute from the root_path
        # - The relative file is relative to the document it is in

        # - it supports globs, so *, index* or *.md works

    # -----------

    # To construct the graph, we only need the relative paths to the
    # Markdown files stored in an efficient structure

    # the myst structured markdown files have the concept of toctree
    # blocks (```{toctree}), these can have the file links. need to be
    # able to find these as well.

    # add a parser that looks for toctree blocks and extracts the files
    # https://sphinx-doc-zh.readthedocs.io/en/latest/markup/toctree.html

    # basically we need a toctree parser or variable added to the
    # MarkdownDocument object
    # all it does is contain the tuple of things that are not keywords
    # can contain:
    # - absolute links <- to the source directory
    # - relative links <- to the document
    # - glob matches

    # would need a method that takes the markdown object and the
    # contents of the toctree and adds links

    # md_links = reverse_relative_links(markdown_files, root=root_path)

    # if document in md_links:
    #     console.print(document)

    # ----
    # We want to build the DAG from the document

    # stop the clock
    search_end_time = time.monotonic_ns()

    console.print()
    # console.print(f"[cyan]Started:  {search_start_time}[/cyan]")
    # console.print(f"[cyan]Finished: {search_end_time}[/cyan]")
    console.print(
        f"[cyan]Elapsed:  {timedelta(microseconds=(search_end_time - search_start_time)/1000)}[/cyan]"
    )
    console.print()

    # # --------
    # markdown_files = find_markdown_files(root_path)

    # # To construct the graph, we only need the relative paths to the
    # # Markdown files stored in an efficient structure

    # md_links = reverse_relative_links(markdown_files, root=root_path)

    # edges = construct_edges(md_links)

    # # At this point we have edges, we can construct the graph
    # console.print("Constructing DAG...")

    # # construct the DAG
    # G = nx.DiGraph()

    # G.add_edges_from(edges)

    # console.print(f"Total Nodes:  {len(G)}")
    # console.print(f"Degree:       {len(G.degree)}")
    # console.print(f"Degree (in):  {len(G.in_degree)}")
    # console.print(f"Degree (out): {len(G.out_degree)}")

    # sub_graph = create_sub_graph(G, incoming_limit=1, outgoing_limit=0)

    # # -----
    # # Plot the Graph

    # console.print("Plotting Graph...")

    # fig = plt.figure(figsize=(15, 10))
    # ax = fig.add_axes((0, 0, 1, 1))

    # g_plot = sub_graph

    # # https://networkx.org/documentation/stable//reference/drawing.html#module-networkx.drawing.layout
    # # Other graph options
    # # kamada_kawai_layout, # this works well <- requires scipy to be installed
    # # shell_layout
    # # circular_layout
    # # planar_layout
    # # spiral_layout
    # # spring_layout

    # nx.draw_networkx(
    #     g_plot,
    #     ax=ax,
    #     pos=nx.spring_layout(g_plot),
    #     with_labels=True,
    #     font_size=10,
    #     font_weight="bold",
    # )

    # plt.show()
