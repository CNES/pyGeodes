#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module deals with all things related to formatting items or collections"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

import json
import warnings

# stdlib imports -------------------------------------------------------
from typing import List, Union

# third-party imports -----------------------------------------------
import geopandas as pd
from shapely.geometry import shape

from pygeodes.utils.consts import (
    COLUMNS_TO_KEEP_FORMATTING_COLLECTIONS,
    COLUMNS_TO_KEEP_FORMATTING_ITEMS,
    GEOPANDAS_DEFAULT_EPSG,
)
from pygeodes.utils.io import write_json

# local imports ---------------------------------------------------
from pygeodes.utils.stac import Collection, Item


def get_from_dico_path(
    path: str, dico: dict
):  # maybe this function could be removed and replaced by a system using jsonpath-ng : https://pypi.org/project/jsonpath-ng/
    """This functions gets a value from a dictionnary using a system of dotted path

    Parameters
    ----------
    path : str
        the dictionnary path
    dico : dict
        the dictionnary

    Examples
    --------

    .. code-block:: python

        dico = {"properties" : {"property_one" : 4}}
        value = get_from_dico_path("properties.property_one",dico) # returns 4


    Returns
    -------
    Any
        the value at path, or None if not found
    """
    if (from_dico := dico.get(path)) is not None:
        return from_dico

    components = path.split(".")
    current_obj = dico
    for component in components:
        if current_obj is None:
            return None
        current_obj = current_obj.get(component)

    return current_obj


def format_collections(
    collections: Union[List[Collection], pd.GeoDataFrame],
    columns_to_add: Union[set, List] = None,
) -> pd.GeoDataFrame:
    """This functions format a list of collections, or a ``GeoDataFrame`` by adding columns by name

    Parameters
    ----------
    collections : Union[List[Collection], pd.GeoDataFrame]
        the list of collections to transform into a dataframe or ``GeoDataFrame`` to add columns to
    columns_to_add : Union[set, List], optional
        the columns to add, by default None

    Returns
    -------
    pd.GeoDataFrame
        the new dataframe
    """
    columns_to_keep = COLUMNS_TO_KEEP_FORMATTING_COLLECTIONS  # par défaut

    if len(collections) == 0:
        return None

    if columns_to_add is not None:
        if len(columns_to_add) > 0:
            columns_to_add = set(columns_to_add)
            columns_to_keep = columns_to_keep.union(columns_to_add)

    if type(collections) is list:
        df = pd.GeoDataFrame()  # we turn a list of collections into a dataframe
    else:
        df = collections  # we add columns to an already made dataframe
        collections = df["collection"].values

    for column_to_keep in columns_to_keep:
        if column_to_keep == "dataType":
            column_to_keep = "id"  # because dataType is equivalent to id but dataType doesn't exist in json

        values = [col.find(column_to_keep) for col in collections]
        if all([value is None for value in values]):
            warnings.warn(
                f"Not adding column {column_to_keep} as no values were found, please be sure it's an existing column"
            )
        else:
            df[column_to_keep] = values

    df["collection"] = collections
    return df


def format_items(
    items: Union[List[Item], pd.GeoDataFrame],
    columns_to_add: Union[set, List] = None,
) -> pd.GeoDataFrame:
    """This functions format a list of items, or a ``GeoDataFrame`` by adding columns by name

    Parameters
    ----------
    items : Union[List[Item], pd.GeoDataFrame]
        the list of items to transform into a dataframe or ``GeoDataFrame`` to add columns to
    columns_to_add : Union[set, List], optional
        the columns to add, by default None

    Returns
    -------
    pd.GeoDataFrame
        the new dataframe
    """
    columns_to_keep = COLUMNS_TO_KEEP_FORMATTING_ITEMS  # par défaut

    if len(items) == 0:
        return None

    if columns_to_add is not None:
        if len(columns_to_add) > 0:
            columns_to_add = set(columns_to_add)
            columns_to_keep = columns_to_keep.union(columns_to_add)

    if type(items) is list:
        df = pd.GeoDataFrame()
    else:
        df = items
        items = df["item"].values

    for column_to_keep in columns_to_keep:
        values = [item.find(column_to_keep) for item in items]
        if all([value is None for value in values]):
            warnings.warn(
                f"Not adding column {column_to_keep} as no values were found, please be sure it's an existing column"
            )
        else:
            df[column_to_keep] = values

    df["item"] = items
    df.set_geometry([shape(item.geometry) for item in items], inplace=True)
    df.set_crs(epsg=GEOPANDAS_DEFAULT_EPSG, inplace=True)  # to use explore

    return df


def export_dataframe(dataframe: pd.GeoDataFrame, outfile: str) -> None:
    """This functions exports a ``pd.GeoDataFrame`` in a file

    Parameters
    ----------
    dataframe : pd.GeoDataFrame
        the dataframe
    outfile : str
        the filepath

    See Also
    --------
    load_dataframe : to load a dataframe from a file
    """
    write_json(json.loads(dataframe.to_json()), outfile)


def load_dataframe(filepath: str):
    """This function loads a ``pd.GeoDataFrame`` from a file

    Parameters
    ----------
    filepath : str
        the file

    Returns
    -------
    pd.GeoDataFrame
        the dataframe

    See Also
    --------
    export_dataframe : to export a dataframe into a file

    """
    from pygeodes.utils.stac import Collection, Item

    df = pd.GeoDataFrame.from_file(filepath)
    if "item" in df.columns:
        df["item"] = [Item.from_dict(item) for item in df["item"].values]
    elif "collection" in df.columns:
        df["collection"] = [
            Collection.from_dict(col) for col in df["collection"].values
        ]
    return df
