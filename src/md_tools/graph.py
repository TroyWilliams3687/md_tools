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
The graph command will display a plot, a DAG, showing the inter-connections
between all of the documents in the system.
"""

# ------------
# System Modules - Included with Python

from pathlib import Path
from datetime import datetime

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
    reverse_relative_links,
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
    "root_path",
    type=click.Path(
        exists=True,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
)
def graph(*args, **kwargs):
    """

    Show the graph connecting all of the documents together.

    # Usage

    $ docs graph /home/troy/repositories/documentation/aegis.documentation.sphinx/docs/source

    """

    root_path = kwargs["root_path"].expanduser().resolve()

    console.print(f"Searching: {root_path}")

    if root_path.is_file():
        console.print("[red]Root path has to be a directory.[/red]")
        ctx.abort()

    search_start_time = datetime.now()

    markdown_files = find_markdown_files(root_path)

    # To construct the graph, we only need the relative paths to the
    # Markdown files stored in an efficient structure

    md_links = reverse_relative_links(markdown_files, root=root_path)

    edges = construct_edges(md_links)

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

    g_plot = sub_graph

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
