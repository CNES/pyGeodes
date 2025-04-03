#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module deals with the main Geodes class"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

import os
import warnings
from pathlib import Path
# stdlib imports -------------------------------------------------------
from typing import List

# third-party imports -----------------------------------------------
from tqdm import tqdm

from pygeodes.utils.config import Config
# local imports ---------------------------------------------------
from pygeodes.utils.consts import (CONFIG_DEFAULT_FILENAME,
                                   GEODES_AVAILABILITY_ENDPOINT,
                                   GEODES_DEFAULT_URL,
                                   GEODES_LIST_PROCESSING_ENDPOINT,
                                   GEODES_PROCESSING_EXECUTION_ENDPOINT,
                                   GEODES_SEARCH_COLLECTIONS_ENDPOINT,
                                   GEODES_SEARCH_ITEMS_ENDPOINT, MAX_NB_ITEMS,
                                   MAX_PAGE_SIZE)
from pygeodes.utils.decorators import requires_api_key
from pygeodes.utils.download import correct_download_tld
from pygeodes.utils.exceptions import (InvalidURLException,
                                       TooManyResultsException)
from pygeodes.utils.formatting import format_collections, format_items
from pygeodes.utils.io import filenames_respecting_regex, write_json
from pygeodes.utils.logger import logger
from pygeodes.utils.profile import (Download, Profile,
                                    load_profile_and_save_download)
from pygeodes.utils.query import full_text_search_in_jsons
from pygeodes.utils.request import (AsyncRequestMaker, SyncRequestMaker,
                                    check_all_different, make_params,
                                    valid_url)
from pygeodes.utils.s3 import create_boto3_client
from pygeodes.utils.s3 import download_item as download_item_from_s3
from pygeodes.utils.stac import Collection, Item


class Geodes:
    _instances = []

    def __init__(self, conf: Config = None, base_url: str = GEODES_DEFAULT_URL):
        if not valid_url(base_url):
            raise InvalidURLException(f"The url {base_url=} is not a valid url")

        if conf is None:
            conf = Config()  # default config
            path = Path(".").resolve().joinpath(CONFIG_DEFAULT_FILENAME)
            if not path.exists():
                write_json(conf.to_dict(), str(path))
                print(
                    f"Has you didn't provide any config, a default config file was created at {str(path)}"
                )

        self.base_url = base_url

        self.set_conf(conf)

        logger.debug(f"New Geodes object instanciated, with {base_url=}")

        Geodes._instances.append(self)

    @classmethod
    def get_last_instance(cls):
        instances = cls._instances
        if len(instances) == 0:
            raise Exception("No instances of geodes were created")
        elif len(instances) == 1:
            return instances[0]
        elif len(instances) > 1:
            warnings.warn(
                f"Geodes was instanciated {len(instances)} times in your program, be aware that it's the last created instance that will be used"
            )
            return instances[-1]

    def set_conf(self, conf: Config):
        self.conf = conf
        logger.setLevel(conf.logging_level)
        self.request_maker = SyncRequestMaker(self.conf.api_key, self.base_url)
        if self.conf.has_s3_parameters():
            self.s3_client = create_boto3_client(self.conf)
        else:
            self.s3_client = None

    def search_collections(
        self,
        full_text_search: str = None,
        query: dict = None,
        return_df: bool = True,
        quiet: bool = False,
    ) -> List[Collection]:

        logger.debug(f"usage of search_collections with query = {query}")
        endpoint = GEODES_SEARCH_COLLECTIONS_ENDPOINT

        params = make_params(query=query, page=1)
        params["limit"] = 500

        logger.debug(f"querying with params : {params}")
        response = self.request_maker.post(endpoint, data=params)
        returned = response.json().get("context").get("returned")

        if full_text_search is not None:

            logger.debug(f"Using full text search")
            collections_jsons = full_text_search_in_jsons(
                response.json().get("collections"),
                full_text_search,
                key_field="id",
                fields_to_index={"description", "title", "id"},
            )
            logger.debug(
                f"Full text search returned {len(collections_jsons)} results"
            )

        else:

            collections_jsons = response.json().get("collections")
            if not len(collections_jsons) == returned:
                warnings.warn(
                    f"Server did not return as many products ({len(collections_jsons)}) as expected ({returned})"
                )

        collections = [
            Collection.from_dict(collection_dict)
            for collection_dict in collections_jsons
        ]

        if return_df:
            query = params.get("query")
            if query:
                context = f"{len(collections)} collection(s) found for query : {query}\n"
                if not quiet:
                    print(context)
                columns_to_add = set(query.keys())
            else:
                columns_to_add = None
            return collections, format_collections(
                collections, columns_to_add=columns_to_add
            )
        else:
            return collections

    def search_items(
        self,
        query: dict = None,
        bbox: List[float] = None,
        intersects: dict = None,
        get_all: bool = False,
        page: int = 1,
        return_df: bool = True,
        quiet: bool = False,
        collections: list[str] = None,
    ) -> List[Item]:

        logger.debug(f"usage of search_items with query = {query}")
        endpoint = GEODES_SEARCH_ITEMS_ENDPOINT

        if bbox is None and query is None and intersects is None:
            raise Exception(
                "Please provide at least 'query' param or 'bbox' or 'intersects' param"
            )

        if get_all:  # we want all results matching the query

            params = make_params(
                query=query,
                page=1,
                bbox=bbox,
                intersects=intersects,
                collections=collections,
            )
            response = self.request_maker.post(endpoint, data=params)
            json_obj = response.json()
            context = json_obj.get("context")
            matched = context.get("matched")
            if not quiet:
                print(f"Found {matched} items matching your query")

            if matched > MAX_NB_ITEMS:
                raise TooManyResultsException(
                    f"Your query matched with {matched} items, which is too much. Please refine your query to be more precise"
                )

            items = [Item.from_dict(dico) for dico in json_obj.get("features")]

            logger.debug(f"making request with {params=}")
            nb_pages_full = matched // MAX_PAGE_SIZE
            rest = matched % MAX_PAGE_SIZE
            if rest > 0:
                nb_pages_full += (
                    1  # we add the last page, even if it's not full
                )

            endpoints = [endpoint for _ in range(2, nb_pages_full + 1)]
            datas = [
                make_params(
                    page=_page,
                    query=query,
                    bbox=bbox,
                    intersects=intersects,
                    collections=collections,
                )
                for _page in range(2, nb_pages_full + 1)
            ]

            # async
            if self.conf.use_async_requests:

                async_rqm = AsyncRequestMaker(self.conf.api_key, self.base_url)
                responses = async_rqm.post(endpoints=endpoints, datas=datas)
                for response in responses:
                    items.extend(
                        [
                            Item.from_dict(dico)
                            for dico in response.get("features")
                        ]
                    )

            else:

                for endpoint, data in tqdm(
                    zip(endpoints, datas), total=len(endpoints), leave=False
                ):
                    response = self.request_maker.post(
                        endpoint=endpoint, data=data
                    )

                    logger.debug(f"making request with {data=}")
                    json_obj = response.json()
                    context = json_obj.get("context")
                    returned = context.get("returned")
                    response_items = json_obj.get("features")

                    if (
                        not len(response_items) == returned
                    ):  # there are as many elements as said in the response
                        warnings.warn(
                            f"Server did not return as many items ({len(items)} != {returned}) as expected, there might be a serverside error"
                        )

                    response_items = [
                        Item.from_dict(item_dict)
                        for item_dict in response_items
                    ]
                    items.extend(response_items)

            if (
                not len(items) == matched
            ):  # there are as many elements as said in the response
                warnings.warn(
                    f"Server did not return as many items ({len(items)} != {matched}) as expected, there might be a serverside error"
                )

            if not check_all_different(items):
                warnings.warn(f"there are duplicate items in your response")

        else:

            params = make_params(
                query=query,
                page=page,
                bbox=bbox,
                intersects=intersects,
                collections=collections,
            )

            logger.debug(f"querying with params : {params}")
            response = self.request_maker.post(endpoint, data=params)
            context = response.json().get("context")
            returned = context.get("returned")
            matched = context.get("matched")
            if not quiet:
                print(
                    f"Found {matched} items matching your query, returning {returned} as get_all parameter is set to False"
                )

            items = [
                Item.from_dict(item_dict)
                for item_dict in response.json().get("features")
            ]

            if not len(items) == returned:
                warnings.warn(
                    f"Server did not return as many items ({len(items)} != {returned}) as expected, there might be a serverside error"
                )

        if return_df:
            query = params.get("query")
            if query:
                context = f"{len(items)} item(s) found for query : {query}\n"
                if not quiet:
                    print(context)
                columns_to_add = set(query.keys())
            else:
                columns_to_add = None
            return items, format_items(items, columns_to_add=columns_to_add)
        else:
            return items

    @requires_api_key(
        bypass_with_s3_credentials=True
    )  # requires api key but can also work with just S3 credentials
    def download_item_archive(self, item: Item, outfile: str = None):
        if outfile is None:

            outfile = item.data_asset.title

            if self.conf.download_dir:
                outfile = Path(self.conf.download_dir).joinpath(outfile)

        else:

            if not os.path.isabs(outfile):
                outfile = Path(self.conf.download_dir).joinpath(outfile)

        if self.s3_client is not None:

            download_for_profile = Download(
                url=item.find("endpoint_url"), destination=outfile
            )
            download_for_profile.start()
            load_profile_and_save_download(download_for_profile)
            outfile_really_used = download_item_from_s3(
                self.s3_client, item, outfile=outfile
            )

        else:

            download_url = correct_download_tld(
                item.data_asset.href
            )  # temp as top level domains aren't ok

            download_for_profile = Download(
                url=download_url, destination=outfile
            )
            download_for_profile.start()
            load_profile_and_save_download(download_for_profile)

            outfile_really_used = self.request_maker.download_file(  # because outfile may change if already used or sth like that
                download_url,
                outfile,
                checksum=item.data_asset_checksum,
                checksum_error=self.conf.checksum_error,
            )

        profile = Profile.load()

        download_for_profile = profile.get_download_from_uuid(
            download_for_profile._id
        )
        download_for_profile.destination = outfile_really_used
        download_for_profile.complete()

        profile.save()

    @requires_api_key(bypass_with_s3_credentials=True)
    def download_item_archives(
        self, items: List[Item], outfiles: List[str] = None
    ):

        if (
            self.conf.use_async_requests and self.s3_client is None
        ):  # can't use async requests with s3_client

            async_rqm = AsyncRequestMaker(self.conf.api_key, self.base_url)
            endpoints = [
                correct_download_tld(item.data_asset.href) for item in items
            ]

            if outfiles is None:

                outfiles = [item.data_asset.title for item in items]

                if self.conf.download_dir:

                    outfiles = [
                        Path(self.conf.download_dir).joinpath(outfile)
                        for outfile in outfiles
                    ]

            else:
                outfiles = [
                    (
                        Path(self.conf.download_dir).joinpath(outfile)
                        if not os.path.isabs(outfile)
                        else outfile
                    )
                    for outfile in outfiles
                ]

            checksums = [item.data_asset.checksum for item in items]
            async_rqm.download_files(endpoints, outfiles, checksums)
            if not outfiles:
                print(f"All downloads completed in {self.conf.download_dir}")

        else:

            if outfiles is None:
                outfiles = [None for item in items]

            if self.s3_client:
                for item, outfile in tqdm(
                    zip(items, outfiles),
                    f"Downloading {len(items)} items from S3",
                ):
                    self.download_item_archive(item, outfile)

            else:

                print(f"Downloading {len(items)} items from geodes")
                for item, outfile in zip(items, outfiles):
                    self.download_item_archive(item, outfile)

    @requires_api_key
    def download_item_files(
        self, item: Item, filenames: List = None, pattern: str = None
    ):
        if filenames is not None and pattern is not None:
            raise Exception(
                f"Can't use filenames parameter and pattern parameter, please use one or the other"
            )
        if filenames is None and pattern is None:
            raise Exception(
                f"Please provide either filenames parameter or pattern parameter"
            )

        archive_url = correct_download_tld(item.data_asset.href)

        if filenames is not None:
            for filename in filenames:
                self.request_maker.extract_file_from_archive(
                    archive_url, filename, self.conf.download_dir
                )

        if pattern is not None:
            filenames = self.list_item_files(item)
            filenames_corresponding_to_pattern = filenames_respecting_regex(
                filenames, pattern
            )
            logger.debug(
                f"found {len(filenames_corresponding_to_pattern)} filenames corresponding to pattern {pattern}"
            )
            for filename in filenames_corresponding_to_pattern:
                self.request_maker.extract_file_from_archive(
                    archive_url, filename, self.conf.download_dir
                )

    @requires_api_key
    def list_item_files(self, item: Item):
        return self.request_maker.list_files_in_archive(
            correct_download_tld(item.data_asset.href)
        )

    @requires_api_key
    def check_item_availability(self, item: Item = None, raw: bool = False):
        name = item.data_asset.title.split(".")[0]
        endpoint = "/".join([GEODES_AVAILABILITY_ENDPOINT, name])
        response = self.request_maker.get(endpoint)
        try:
            dico = response.json()
        except Exception:
            raise Exception(f"There was an error while checking availability")
        if raw:
            return dico
        else:
            res = {}
            for file in dico.get("files"):
                checksum = file.get("checksum")
                string = (
                    "available" if file.get("available") else "not available"
                )

                if checksum == item.data_asset_checksum:
                    res["data"] = string
                else:
                    res["quicklook"] = string
            return res

    @requires_api_key
    def list_available_processes(self, raw: bool = False):
        endpoint = GEODES_LIST_PROCESSING_ENDPOINT
        response = self.request_maker.get(endpoint)
        processes = response.json()
        if raw:
            return processes
        else:
            return [process.get("id") for process in processes.get("processes")]

    @requires_api_key
    def start_process(self, item: Item, process_id: str):
        # maybe check here that this process id is in available processes
        endpoint = GEODES_PROCESSING_EXECUTION_ENDPOINT.format(
            process_id=process_id
        )
        warnings.warn(f"This method is not impletented completely")
        data = {
            "inputs": {
                # TODO ajouter apiKey en Header de la requête
                "product-title": item.data_asset.title.split(".")[0],
                "notif-email": True,
                "timeout": 15,
            }
        }
        response = self.request_maker.post(
            endpoint, data=data, headers={"Prefer": "respond-async"}
        )
        return response
