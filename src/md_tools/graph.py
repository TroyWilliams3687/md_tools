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
from collections.abc import Sequence
from typing import Optional
from queue import SimpleQueue

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
    # reverse_relative_links,
)

from md_tools.myst import (
    inside_toctree,
    toctree_links,
)


# -------------

def get_relative_links(
        document:MarkdownDocument,
        root:Optional[Path]=None,
    ) -> Optional[set[Path]]:
    """
    """

    if root:
        links = set()

        for rl in document.relative_links:
            for link in rl.matches:
                if link.url.startswith("/"):
                    links.add(Path(link.url[1:]))

                else:
                    full_url = document.filename.parent / Path(link.url)
                    links.add(full_url.relative_to(root))

    else:
        links = set(
            link.url for rl in document.relative_links for link in rl.matches
        )

    # should the link.url be absolute to the root?

    for line in inside_toctree(document.contents, directive_name="toctree"):

        discovered_links = toctree_links(line.line, document.filename, root)

        if discovered_links:
            for dl in discovered_links:

                if root:
                    links.add(dl.relative_to(root))
                else:
                    links.add(dl)

    return links if links else None


def reverse_relative_links(
        md_files: Sequence[MarkdownDocument],
        root: Path = None,
    ) -> dict[str, set[Path]]:
    """
    Given a sequence of MarkdownDocument objects, construct a dictionary
    keyed by the filename of the document storing the list of relative
    links within the document.

    # Return

    a dictionary

    """

    md_link_lookup = {}

    for md in md_files:

        key = str(md.filename.relative_to(root)) if root else str(md.filename)
        md_link_lookup[key] = get_relative_links(md, root)

    return md_link_lookup


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
    console.print(f'Files Found:      {len(markdown_files)}')


    md_links = reverse_relative_links(markdown_files, root=root_path)
    console.print(f'Files with Links: {len(md_links)}')

    # NOTE: the number of markdown files should equal the number of
    # markdown files with links.

    # for mdl in md_links:
    #     console.print(f'{mdl}')
        # console.print(f'{mdl}:{md_links[mdl]}')

    # ----
    # construct the edges of the graphs from the root node

    keys = SimpleQueue() # documents to search
    edges = [] # contains the tuples that define the edges
    processed = set() # did we already see the document

    md = MarkdownDocument(root_path / document)

    # add the first document
    keys.put(str(md.filename.relative_to(root_path)))

    while not keys.empty():

        k = keys.get()
        processed.add(k)

        if k in md_links and md_links[k]:

            for node in md_links[k]:

                node_key = str(node)

                console.print(f'[cyan]EDGE:[/cyan] [green]{k} -> {node_key}[/green]')

                edges.append((k, node_key))

                if node_key not in processed:
                    keys.put(node_key)

    # ----
    console.print()
    console.print(f'Edges = {len(edges)}')

    # At this point we have edges, we can construct the graph
    console.print("Constructing DAG...")

    # construct the DAG
    G = nx.DiGraph()

    G.add_edges_from(edges)

    console.print(f"Total Nodes:  {len(G)}")
    console.print(f"Degree:       {len(G.degree)}")
    console.print(f"Degree (in):  {len(G.in_degree)}")
    console.print(f"Degree (out): {len(G.out_degree)}")

    sub_graph = create_sub_graph(G, incoming_limit=1, outgoing_limit=0)

    # -----
    # Plot the Graph

    console.print("Plotting Graph...")

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_axes((0, 0, 1, 1))

    g_plot = G #sub_graph

    # https://networkx.org/documentation/stable//reference/drawing.html#module-networkx.drawing.layout
    # Other graph options
    # kamada_kawai_layout, # this works well <- requires scipy to be installed
    # shell_layout
    # circular_layout
    # planar_layout
    # spiral_layout
    # spring_layout

    nx.draw_networkx(
        g_plot,
        ax=ax,
        pos=nx.spring_layout(g_plot),
        with_labels=True,
        font_size=10,
        font_weight="bold",
    )

    plt.show()


    # stop the clock
    search_end_time = time.monotonic_ns()

    console.print()
    console.print(
        f"[cyan]Elapsed:  {timedelta(microseconds=(search_end_time - search_start_time)/1000)}[/cyan]"
    )
    console.print()


