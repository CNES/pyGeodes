#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""argparser.py

[your module's docstring]

"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import argparse

# local imports ---------------------------------------------------
from pygeodes._info import author, description, name, version

# third-party imports -----------------------------------------------


def parse_args():
    prog = f"{name} v{version} : {description} ({author})"
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument(
        "-v",
        "--version",
        help="to display the current version of the tool",
        action="store_true",
    )

    subparsers = parser.add_subparsers(dest="command")
    help_arg_query = "the search query you want to use, it can be a filepath to a json or a json directly in the command"

    # search
    search = subparsers.add_parser(
        "search",
        help="the command allowing you to search through geodes",
    )

    parser.add_argument(
        "--config",
        help="the path to the config file you want to use",
        required=False,
        type=str,
    )

    search.add_argument(
        "-c",
        "--collections",
        type=str,
        help="the collection of the item you want to search",
    )

    search.add_argument(
        "-cs",
        "--collections_search",
        type=str,
        help="allows you to search in collections instead of items, providing a search term that will be used to search in full text",
    )

    search.add_argument(
        "--start-date",
        type=str,
        help="the lower bound of the acquisition date of the item you want to search",
    )
    search.add_argument(
        "--end-date",
        type=str,
        help="the upper bound of the acquisition date of the item you want to search",
    )
    search.add_argument(
        "--data-type",
        type=str,
        help="the data type of the item you want to search",
    )

    search.add_argument(
        "-q",
        "--query",
        required=False,
        help=help_arg_query,
    )

    search.add_argument(
        "-b",
        "--bbox",
        nargs=4,
        required=False,
        help="a bounding box in which you could want to search, e.g. : 1.3 44.6 2.1 44.9",
    )
    search.add_argument(
        "-o",
        "--output",
        required=False,
        help="the json file to export the results to, if not specified results will just be displayed",
    )
    search.add_argument(
        "--download", action="store_true", help="wether to download the results"
    )

    # download
    download = subparsers.add_parser(
        "download",
        help="the command allowing you to download an item from its id",
    )

    download.add_argument("id", help="the id of the item you want to download")
    download.add_argument("--api-key", help="your geodes api key")

    # watch_downloads
    watch_downloads = subparsers.add_parser(
        "watch-downloads",
        help="the command allowing you to monitor all current and pending downloads on your instance of pygeodes",
    )
    watch_downloads.add_argument(
        "-r",
        "--rate",
        type=int,
        help="the refresh rate (in seconds) of the display",
        default=5,
    )
    watch_downloads.add_argument(
        "-s",
        "--simplified",
        help="wether to use the simplified version of the display (may help better rendering on some terminals)",
        action="store_true",
    )

    return parser.parse_args()
