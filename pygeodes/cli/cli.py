#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cli.py

[your module's docstring]

"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import sys

from rich.console import Console

# third-party imports -----------------------------------------------
from rich.status import Status
from rich.syntax import Syntax

from pygeodes._info import version

# local imports ---------------------------------------------------
from pygeodes.cli.argparser import parse_args
from pygeodes.cli.cli_utils import (
    deal_with_query_and_conf,
    table_from_dataframe,
)
from pygeodes.geodes import Geodes
from pygeodes.utils.config import Config
from pygeodes.utils.datetime_utils import complete_datetime_from_str
from pygeodes.utils.formatting import export_dataframe, format_items
from pygeodes.utils.io import file_exists
from pygeodes.utils.profile import Profile


def watch_downloads(args):
    Profile.watch_downloads(refresh_rate=args.rate, simplified=args.simplified)


def download(args):
    if args.api_key is not None:
        geodes = Geodes(conf=Config(api_key=args.api_key))
    else:
        geodes = Geodes(conf=args.conf)
    items = geodes.search_items(
        query={"identifier": {"eq": args.id}},
        quiet=True,
        return_df=False,
        get_all=False,
    )
    if len(items) > 1:
        print(f"This id is not precise enough, it returns multiple results")
        sys.exit(1)
    elif len(items) == 1:
        geodes.download_item_archive(items[0])
        exit()
    elif len(items) == 0:
        print(f"This id doesn't return any results")
        sys.exit(1)


def search(args):
    geodes, query_dict = deal_with_query_and_conf(args)
    console = Console()
    if args.collections_search:

        with Status(
            f"Searching collections with search term = {args.collections_search}"
        ):
            collections, dataframe = geodes.search_collections(
                full_text_search=args.collections_search
            )

        if args.output:
            if dataframe is not None:
                export_dataframe(dataframe, args.output)
                print(f"Output exported in json format to {args.output}")
            else:
                print(
                    f"No dataframe was exported has query didn't return any collection"
                )
            exit()
        title = f"Collections found for search term = {args.collections_search} ({len(collections)} in table)"
        table = table_from_dataframe(dataframe, title=title)
        console.print(table)

    else:

        get_all = False
        if args.output:
            get_all = True

        if not query_dict:
            query_dict = {}
            """if args.id:
                query_dict["id"] = {"eq" : args.id}"""
            if args.data_type:
                query_dict["dataType"] = {"eq": args.data_type}
            date_arg = "end_datetime"  # we arbitrarily chose to consider endDate as the date, as startDate and endDate are usually really close -> TODO
            if args.start_date or args.end_date:
                query_dict[date_arg] = {}
            if args.start_date:
                query_dict[date_arg]["gte"] = complete_datetime_from_str(
                    args.start_date
                )
            if args.end_date:
                query_dict[date_arg]["lte"] = complete_datetime_from_str(
                    args.end_date
                )

        with Status(
            f"Searching items with bbox={args.bbox} and query={query_dict}"
        ):

            items, dataframe = geodes.search_items(
                query=query_dict,
                bbox=args.bbox,
                get_all=get_all,
                collections=args.collections.strip().split(",") if args.collections is not None else None,
            )

        dataframe = format_items(dataframe, {"identifier"})
        dataframe["id"] = dataframe["identifier"]
        dataframe = dataframe.drop(columns=["identifier"])

        if args.output:
            if dataframe is not None:
                export_dataframe(dataframe, args.output)
                print(f"Output exported in json format to {args.output}")
            else:
                print(
                    f"No dataframe was exported has query didn't return any item"
                )
            exit()

        code = """
        from pygeodes import Geodes
        geodes = Geodes()
        items,dataframe = geodes.search_items(query={query_dict},bbox={bbox},get_all=True)
        """.format(
            query_dict=query_dict, bbox=args.bbox
        )

        code = Syntax(code, line_numbers=False, lexer="python", word_wrap=True)

        title = f"Items found for bbox={args.bbox=} and query={query_dict} ({len(items)} in table)"
        table = table_from_dataframe(dataframe, title=title)
        console.print(table)
        console.print(
            f"Note : this is an overview of the results, if you want the complete output :",
            style="bold",
        )
        console.print(
            f"1. Use parameter -o, --output with a json filepath to export the results to"
        )
        console.print("\nOr\n", style="italic")
        console.print(
            f"2. Copy this code and get started in a python script : \n"
        )
        console.print(code)

        if args.download:
            console.print(
                f"Starting download of result products ({len(items)} items)"
            )
            geodes.download_item_archives(items)


def cli():
    args_parsed = parse_args()

    if args_parsed.version:
        print(version)
        exit()

    if args_parsed.config:
        if file_exists(args_parsed.config):
            conf = Config.from_file(args_parsed.config)
    else:
        conf = Config()

    args_parsed.conf = conf

    command = args_parsed.command
    functions = {
        func.__name__.replace("_", "-"): func
        for func in [watch_downloads, search, download]
    }
    func_to_call = functions.get(command)
    if func_to_call is None:
        raise Exception(
            f"This command doesn't exist, availables : {list(functions.keys())}"
        )
    else:
        func_to_call(args_parsed)
