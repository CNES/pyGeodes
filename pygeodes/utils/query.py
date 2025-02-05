#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains the Query class"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

import warnings
from time import perf_counter

# stdlib imports -------------------------------------------------------
from typing import List

from tqdm import tqdm
from whoosh.fields import NGRAM, STORED, TEXT, Schema

# third-party imports -----------------------------------------------
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import MultifieldParser, OrGroup

# local imports ---------------------------------------------------
from pygeodes.utils.consts import (
    KNOWN_COLLECTION_REQUESTABLE_ARGUMENTS,
    KNOWN_ITEM_REQUESTABLE_ARGUMENTS,
    REQUESTABLE_ARGS_FILEPATH,
)
from pygeodes.utils.io import load_json
from pygeodes.utils.logger import logger


def get_requestable_args():
    return load_json(REQUESTABLE_ARGS_FILEPATH)


class Argument:
    def __init__(self, name: str):
        self.name = name
        self.queries = {}

    def eq(self, value):
        self.queries["eq"] = value

    def lte(self, value):
        self.queries["lte"] = value

    def gte(self, value):
        self.queries["gte"] = value

    def contains(self, value):
        self.queries["contains"] = value

    def is_in(self, value: list):
        if not type(value) is list:
            raise Exception(
                f"is_in argument must be a list type, not {type(value)}"
            )
        self.queries["in"] = value

    def to_dict(self):
        return self.queries


class Query:
    def __init__(self):
        self.args: List[Argument] = []

    def add(self, argument: Argument):
        self.args.append(argument)

    def check(self):
        names = [arg.name for arg in self.args]
        for name in names:
            if (count := names.count(name)) > 1:
                raise Exception(
                    f"Argument {name} appears {count} times in your query"
                )

    def check_for_collection(self):
        self.check()
        for arg in self.args:
            if arg.name not in KNOWN_COLLECTION_REQUESTABLE_ARGUMENTS:
                raise Exception(
                    f"Argument {arg.name} cannot be queried in collections"
                )

    def check_for_item(self):
        self.check()
        for arg in self.args:
            if arg.name not in KNOWN_ITEM_REQUESTABLE_ARGUMENTS:
                raise Exception(
                    f"Argument {arg.name} cannot be queried in items"
                )

    def to_dict(self):
        dico = {}
        for arg in self.args:
            dico[arg.name] = arg.to_dict()


def full_text_search_in_jsons(
    jsons: List[dict],
    search_term: str,
    key_field: str,
    fields_to_index: set,
    return_index: bool = False,
):
    from pygeodes.utils.formatting import (
        get_from_dico_path,
    )  # to avoid circular import

    begin = perf_counter()

    # verifications
    for json_obj in jsons:
        assert (
            get_from_dico_path(key_field, json_obj) is not None
        ), f"{key_field=} has value None"
        for field_to_index in fields_to_index:
            assert (
                get_from_dico_path(field_to_index, json_obj) is not None
            ), f"{field_to_index=} has value None {json_obj=}"

    dico = {
        get_from_dico_path(key_field, json_obj): json_obj for json_obj in jsons
    }

    with warnings.catch_warnings():  # because sometimes whoosh raises a unexpected warning
        schema_components = {
            field: TEXT if field != "id" else NGRAM for field in fields_to_index
        }
        if key_field in fields_to_index:
            if key_field != "id":
                schema_components[key_field] = TEXT(stored=True)
            else:
                schema_components[key_field] = NGRAM(
                    minsize=3, stored=True, field_boost=10.0
                )
        else:
            schema_components[key_field] = STORED
        schema = Schema(**schema_components)
        ix = RamStorage().create_index(schema)
        writer = ix.writer()
        for json_obj in tqdm(dico.values(), "Indexing"):

            to_add = {
                field: str(get_from_dico_path(field, json_obj))
                for field in fields_to_index
            }
            to_add[key_field] = str(get_from_dico_path(key_field, json_obj))
            writer.add_document(**to_add)
        writer.commit()

        query = MultifieldParser(
            [field for field in fields_to_index], ix.schema, group=OrGroup
        )

        with ix.searcher() as searcher:
            query = query.parse(search_term)
            results = searcher.search(query, terms=True, limit=None)
            logger.debug(
                f"Matched terms for {search_term=} : {results.matched_terms()}"
            )
            ids = [result.get(key_field) for result in results]

    res = [dico.get(_id) for _id in ids]

    end = perf_counter()
    logger.debug(
        f"Proceeded to full-text search on {len(jsons)} objects in {end - begin} seconds"
    )

    if return_index:
        return res, ix
    else:
        return res


def full_text_search(objects, search_term, return_index: bool = False):
    types = set([type(obj) for obj in objects])
    if len(types) != 1:
        raise Exception(
            f"full_text_search doesn't work with mixed objects types, use either only Item objs, either only Collection objs"
        )

    _type = list(types)[0]

    available_keys = objects[0].list_available_keys(with_origin=True)
    for obj in objects:
        available_keys = available_keys.intersection(
            obj.list_available_keys(with_origin=True)
        )  # with_origin param allow to get full dico path, not shortcut available by Item.find or Collection.find

    jsons = [obj.to_dict() for obj in objects]

    logger.debug(
        f"Proceeding to full-text search for term {search_term} on fields {available_keys}"
    )

    results = full_text_search_in_jsons(
        jsons, search_term, "id", available_keys, return_index=return_index
    )

    if return_index:

        return [_type.from_dict(json_obj) for json_obj in results[0]], results[
            1
        ]

    else:

        return [_type.from_dict(json_obj) for json_obj in results]
