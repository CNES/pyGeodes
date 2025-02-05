import json
from argparse import Namespace

from rich.table import Table

from pygeodes.geodes import Geodes
from pygeodes.utils.io import file_exists, load_json


def deal_with_query_and_conf(args: Namespace):
    if args.query is not None:
        query = args.query
        is_dico = False
        try:
            query_dict = json.loads(query)
            is_dico = True
        except:
            pass

        is_file = file_exists(query, False)
        if not is_file and not is_dico:
            raise Exception(
                f"Your input for parameter query couldn't be parsed as filepath or query json (query_found = {query})"
            )

        if is_file:
            query_dict = load_json(query)
    else:
        query_dict = None

    conf = args.conf
    geodes = Geodes(conf=conf)
    return geodes, query_dict


def table_from_dataframe(dataframe, title: str = "Search results"):
    table = Table(title=title, expand=True)

    if dataframe is not None:

        if "item" in dataframe.columns:
            dataframe = dataframe.drop(
                columns=["item", "geometry"]
            )  # items dataframe
        else:
            dataframe = dataframe.drop(columns=["title"])  #
            dataframe["collection"] = (
                dataframe["collection"].apply(lambda x: x.id).astype(str)
            )
            # dataframe = dataframe.drop(
            #     columns=["collection"]
            # )  # collections dataframe

        for column in dataframe.columns:
            table.add_column(column)

        for tp in dataframe.values:
            tp_transtyped = [str(element) for element in tp]
            table.add_row(*tp_transtyped)

    return table
