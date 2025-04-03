#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module deals with all classes derived from pystac https://pystac.readthedocs.io/en/stable/"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------
import os
import base64

# stdlib imports -------------------------------------------------------
import warnings

from IPython.display import Image, display
from pystac.asset import Asset as StacAsset

# third-party imports -----------------------------------------------
from pystac.collection import Collection as StacCollection
from pystac.item import Item as StacItem

from pygeodes.utils.consts import CORRECT_STAC_VERSION
from pygeodes.utils.exceptions import (
    DataAssetMissingException,
    RequiresApiKeyException,
)

# local imports ---------------------------------------------------
from pygeodes.utils.query import Query


def correct_stac_version(collection_dict: dict) -> dict:
    collection_dict["stac_version"] = CORRECT_STAC_VERSION
    return collection_dict


def get_keys_from_dict(dico):
    keys = []
    for key, value in dico.items():
        if type(value) is dict:
            keys.extend(
                [f"{key}.{subkey}" for subkey in get_keys_from_dict(value)]
            )
        else:
            keys.append(key)

    return keys


class Collection(StacCollection):

    @classmethod
    def from_stac_collection(cls, collection: StacCollection):
        return Collection.from_dict(collection.to_dict())

    @classmethod
    def from_dict(cls, dico: dict):
        return super().from_dict(correct_stac_version(dico))

    def to_dict(self):
        return super().to_dict(transform_hrefs=False) # TODO

    def find(self, key: str):
        from pygeodes.utils.formatting import get_from_dico_path

        return get_from_dico_path(key, self.to_dict())

    def list_available_keys(self):
        dico = self.to_dict()
        return set(get_keys_from_dict(dico))


class Asset(StacAsset):

    def __str__(self):
        return f"Asset(title={self.title},roles={self.roles})"

    @classmethod
    def from_stac_asset(cls, asset: StacAsset):
        return Asset.from_dict(asset.to_dict())

    @property
    def filesize(self):
        return int(
            self.description.split("\n")[0]
            .replace(" bytes", "")
            .replace("File size: ", "")
        )

    @property
    def checksum(self):
        return self.description.split("Checksum MD5: ")[-1].strip()


class Item(StacItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_used: Query = None
        self.assets = {
            key: Asset.from_stac_asset(value)
            for key, value in self.assets.items()
        }

    @property
    def s3_path(self):
        return self.find("accessService:endpointURL")

    def download_archive(self, outfile: str = None):
        from pygeodes.geodes import Geodes

        geodes = Geodes.get_last_instance()
        geodes.download_item_archive(item=self, outfile=outfile)
        
    @classmethod
    def from_dict(cls, dico: dict):
        return super().from_dict(correct_stac_version(dico))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Item ({self.id})"

    def _repr_html_(self):
        return self.__repr__()

    def __json__(self):
        return self.to_dict()

    @property
    def filesize(self):
        return self.data_asset.filesize

    def to_dict(self):
        return super().to_dict(transform_hrefs=False)

    def list_available_keys(self, with_origin=False):
        dico = self.to_dict()
        properties = dico.get("properties")
        keys = ["id"]
        if with_origin:
            keys.extend(
                [f"properties.{key}" for key in get_keys_from_dict(properties)]
            )
        else:
            keys.extend(get_keys_from_dict(properties))
        return set(keys)

    def find(self, key: str):
        dico = self.to_dict()
        if key in ["id", "type", "collection"]:
            return dico.get(key)

        from pygeodes.utils.formatting import get_from_dico_path

        return get_from_dico_path(key, dico.get("properties"))

    @property
    def data_asset(self):
        possible_data_asset = []
        # Get all "data" assets
        for asset in self.assets.values():
            if "data" in asset.roles:
                possible_data_asset.append(asset)
        # Prefer zip file as data asset
        for asset in possible_data_asset:
            if os.path.splitext(asset.title)[-1] == ".zip":
                return asset
        # Get the first one if not zip file found
        if len(possible_data_asset) > 0:
            return possible_data_asset[0]

        raise DataAssetMissingException(
            f"The item {self.id} has no data asset (has assets : {self.assets.values()})"
        )

    @property
    def quicklook_asset(self):
        for asset in self.assets.values():
            if "overview" in asset.roles:
                return asset

        return None

    def get_quicklook_content_in_base64(self):
        from pygeodes.geodes import Geodes
        from pygeodes.utils.download import correct_download_tld

        geodes = Geodes.get_last_instance()
        url = correct_download_tld(self.quicklook_asset.href)
        response = geodes.request_maker.get(url)
        return base64.b64encode(response.content).decode("utf-8")

    def show_quicklook(self):
        asset = self.quicklook_asset
        if asset:
            from pygeodes.geodes import Geodes
            from pygeodes.utils.download import correct_download_tld

            geodes = Geodes.get_last_instance()
            if not geodes.conf.has_api_key:
                raise RequiresApiKeyException(
                    f"show_quicklook requires an api key, please provide one using configuration"
                )

            try:
                url = correct_download_tld(asset.href)
                response = geodes.request_maker.get(url)
                # image_bytes = BytesIO(response.content)
                display(Image(data=response.content))
            except Exception as e:
                warnings.warn(
                    f"Unable to display quicklook for this item ({e})"
                )
        else:
            warnings.warn(f"No quicklook asset for this item")

    @property
    def data_asset_checksum(self):
        if (data_asset := self.data_asset) is not None:
            return data_asset.checksum
        else:
            return None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        else:
            return self.id == other.id
