#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains all things related to download monitoring and download queues in pygeodes
"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

import os
import warnings

# stdlib imports -------------------------------------------------------
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import List, Literal
from uuid import uuid4

# third-party imports -----------------------------------------------
from rich.live import Live
from rich.table import Table
from tqdm import tqdm

from pygeodes.utils.consts import PROFILE_DEFAULT_PATH
from pygeodes.utils.dataclasses_utils import class_from_args
from pygeodes.utils.datetime_utils import (
    a_week_ago,
    datetime_to_str,
    str_to_datetime,
    time_ago,
    today,
)
from pygeodes.utils.download import correct_download_tld

# local imports ---------------------------------------------------
from pygeodes.utils.io import compute_md5, file_exists, load_json, write_json
from pygeodes.utils.logger import logger
from pygeodes.utils.s3 import download_item as download_item_from_s3
from pygeodes.utils.stac import Item


@dataclass
class Download:
    """This class represents a pending, current or finished Geodes download"""

    url: str
    destination: str = None
    _started_at: str = None
    _completed_at: str = None
    _id: str = None

    def __post_init__(self):
        """This function is executed after instanciating a Download objects and corrects some behaviors"""
        if self._id is None:
            self._id = str(uuid4())

        if self.destination:
            self.destination = str(self.destination)

        if type(self._started_at) is datetime:
            self._started_at = datetime_to_str(self._started_at)

        if type(self._completed_at) is datetime:
            self._completed_at = datetime_to_str(self._completed_at)

    def start(self):
        """This method starts the download (sets _started_at to now)"""
        if self._started_at is None:
            self._started_at = datetime_to_str(datetime.now())

    @classmethod
    def from_dict(cls, dico: dict):
        """This function creates a Download object from a dictionnary

        Parameters
        ----------
        dico : dict
            a dictionnary representing a Download object

        """
        return class_from_args(cls, dico)

    @property
    def started_at(self):
        """This returns _started_at as a datetime object

        Returns
        -------
        datetime
            started_at
        """
        if self._started_at is not None:
            return str_to_datetime(self._started_at)
        else:
            return None

    @property
    def completed_at(self):
        """This returns _completed_at as a datetime object

        Returns
        -------
        datetime
            completed_at
        """
        if self._completed_at is not None:
            return str_to_datetime(self._completed_at)
        else:
            return None

    @property
    def time_taken(self):
        """This returns the time taken to download if the download is completed

        Returns
        -------
        datetime
            the time taken
        """
        if not self.completed_at:
            return None
        else:
            return self.completed_at - self.started_at

    def to_dict(self):
        dico = asdict(self)
        dico["destination"] = str(dico["destination"])
        return dico

    def complete(self):
        """This sets the _completed_at attr to now"""
        self._completed_at = datetime_to_str(datetime.now())

    def __eq__(self, obj):
        return obj._id == self._id

    def __hash__(self):
        return hash(self._id)


class Profile:
    _filepath = PROFILE_DEFAULT_PATH

    def __init__(self):
        self.downloads = {}

    def get_download_from_uuid(self, uuid):
        return self.downloads.get(uuid)

    @classmethod
    def reset(cls):
        if file_exists(cls._filepath, False):
            os.remove(cls._filepath)

    @classmethod
    def load(cls):
        if not file_exists(cls._filepath, False):
            write_json({"downloads": {}}, cls._filepath)

        content = load_json(cls._filepath)
        obj = cls()
        obj.downloads = {
            key: Download.from_dict(value)
            for key, value in content.get("downloads").items()
        }
        return obj

    def add_download(self, download: Download):
        self.downloads[download._id] = download

    @property
    def nb_downloads(self):
        return len(self.downloads)

    @classmethod
    def watch_downloads(cls, refresh_rate: float = 5, simplified: bool = False):
        try:
            if simplified:
                while True:
                    profile = Profile.load()
                    current_downloads = profile.current_downloads()
                    pending_downloads = profile.pending_downloads()

                    print(
                        f"[{datetime.now()}] Current downloads : {len(current_downloads)} | Pending downloads : {len(pending_downloads)}"
                    )
                    sleep(refresh_rate)
            else:

                started = datetime.now()

                def create_table():
                    table = Table(
                        caption=f"[bold orange1]Current[/bold orange1], [bold red]pending[/bold red] and [bold green]just finished downloads[/bold green] (refreshing every {refresh_rate} seconds, started watching {time_ago(started)})",
                        expand=True,
                        show_lines=True,
                    )
                    table.add_column("Download ID")
                    table.add_column("URL")
                    table.add_column("Destination")
                    table.add_column("Started at")
                    table.add_column("Completed at")
                    return table

                with Live(
                    create_table(), refresh_per_second=refresh_rate
                ) as live:
                    while True:
                        table = create_table()
                        profile = cls.load()

                        pending_downloads = profile.pending_downloads()
                        current_downloads = profile.current_downloads()
                        just_finished = profile.just_finished_downloads(
                            nb_seconds=refresh_rate * 2
                        )  # times two to be sure we get to see the finished downloads

                        for download in just_finished:
                            elements = [
                                download._id,
                                download.url,
                                download.destination,
                                f"{str(download.started_at)} ({time_ago(download.started_at)})",
                                f"{str(download.completed_at)} ({time_ago(download.completed_at)})",
                            ]
                            elements = [
                                f"[green]{element}" for element in elements
                            ]
                            table.add_row(*elements)

                        for download in current_downloads:
                            elements = [
                                download._id,
                                download.url,
                                download.destination,
                                f"{str(download.started_at)} ({time_ago(download.started_at)})",
                                "",
                            ]
                            elements = [
                                f"[orange1]{element}" for element in elements
                            ]
                            table.add_row(*elements)

                        for download in pending_downloads:
                            elements = [
                                download._id,
                                download.url,
                                download.destination,
                                "",
                                "",
                            ]
                            elements = [
                                f"[red]{element}" for element in elements
                            ]
                            table.add_row(*elements)

                        live.update(table)
                        sleep(refresh_rate)

        except KeyboardInterrupt:
            print("Download watching interrupted")

    def current_downloads(self):
        return {
            download
            for download in self.downloads.values()
            if download.completed_at is None and download.started_at is not None
        }

    def pending_downloads(self):
        return {
            download
            for download in self.downloads.values()
            if download.started_at is None
        }

    def just_finished_downloads(self, nb_seconds):
        if nb_seconds < 1:
            nb_seconds = 1

        def is_recent(date):
            now = datetime.now()
            end = now
            begin = now - timedelta(seconds=nb_seconds)
            return begin <= date <= end

        finished = {
            download
            for download in self.downloads.values()
            if download.completed_at is not None
        }
        return {
            download
            for download in finished
            if is_recent(download.completed_at)
        }

    def recent_downloads(self, since: Literal["today", "this_week"] = "today"):
        if since == "today":
            begin, end = today()
        elif since == "this_week":
            begin = a_week_ago()
            end = datetime.now()
        else:
            raise Exception(
                f"Please use one of 'today','this_week' as 'since' parameter"
            )

        def is_in_interval(obj):
            if obj.completed_at:
                return (
                    begin <= obj.completed_at <= end
                    or begin <= obj.started_at <= end
                )
            else:
                return begin <= obj.started_at <= end

        print(f"Displaying downloads from {begin} to {end}")
        return [
            download
            for download in self.downloads.values()
            if is_in_interval(download)
        ]

    def to_dict(self):
        dico = {}
        dico["nb_downloads"] = self.nb_downloads
        dico["downloads"] = {
            key: value.to_dict() for key, value in self.downloads.items()
        }
        return dico

    def save(self):
        logger.debug(f"saving profile as {self.to_dict()}")
        write_json(self.to_dict(), self._filepath)


def load_profile_and_save_download(d: Download):
    profile = Profile.load()
    profile.add_download(d)
    profile.save()


class DownloadQueue:
    def __init__(self, items: List[Item], download_dir: str = None):
        self.items = items
        self.downloads_objects = {}
        from pygeodes.geodes import Geodes

        self.geodes_instance = Geodes.get_last_instance()
        if download_dir:
            self.download_dir = download_dir
        else:
            self.download_dir = self.geodes_instance.conf.download_dir

    def _download_item(self, item: Item):
        download_for_profile = self.downloads_objects[item]
        outfile = str(Path(self.download_dir).joinpath(item.data_asset.title))
        download_for_profile.destination = outfile

        if self.geodes_instance.s3_client is not None:

            download_for_profile.url = item.find("accessService:endpointURL")
            download_for_profile.start()
            load_profile_and_save_download(download_for_profile)

            outfile_really_used = download_item_from_s3(
                self.geodes_instance.s3_client, item, outfile=outfile
            )

        else:

            download_url = correct_download_tld(
                item.data_asset.href
            )  # temp as top level domains aren't ok

            download_for_profile.url = download_url
            download_for_profile.start()
            load_profile_and_save_download(download_for_profile)

            outfile_really_used = self.geodes_instance.request_maker.download_file(  # because outfile may change if already used or sth like that
                download_url,
                outfile,
                checksum=item.data_asset_checksum,
                checksum_error=self.geodes_instance.conf.checksum_error,
                verbose=False,
            )

        profile = Profile.load()

        download_for_profile = profile.get_download_from_uuid(
            download_for_profile._id
        )
        download_for_profile.destination = outfile_really_used
        self.downloads_objects[item] = download_for_profile
        download_for_profile.complete()

        profile.save()

    def _init_downloads(self):
        if len(self.downloads_objects) == 0:
            profile = Profile.load()
            for item in self.items:
                d = Download(
                    url=item.data_asset.href, destination=None, _started_at=None
                )
                self.downloads_objects[item] = d
                profile.add_download(d)
            profile.save()

    def check_integrity(self):
        for item, download in self.downloads_objects.items():
            if download.completed_at is not None:
                checksum = item.data_asset.checksum
                if file_exists(download.destination, False):
                    checksum_at_destination = compute_md5(download.destination)
                    if checksum != checksum_at_destination:
                        warnings.warn(
                            f"File for item {item} doesn't correspond to checksum"
                        )
                else:
                    warnings.warn(
                        f"File is absent at destination for item {item}"
                    )
            else:
                warnings.warn(f"Download for item {item} was not completed")

    def run(self):
        self._init_downloads()
        downloads = self.downloads_objects.values()
        if all([value.completed_at is not None for value in downloads]):
            print(f"All downloads are completed in {self.download_dir}")
            return

        completed = [
            download
            for download in downloads
            if download.completed_at is not None
        ]
        pending = [
            download
            for download in downloads
            if download.completed_at is None and download.started_at is None
        ]
        print(
            f"Queue (started {datetime.now()}) | Completed : {len(completed)} | Pending : {len(pending)}"
        )

        for item in tqdm(self.items):
            obj = self.downloads_objects[item]
            if obj.completed_at is None:
                if (
                    obj.started_at is not None and obj.destination is not None
                ):  # was started but not completed, file is not complete, so we start again
                    if file_exists(obj.destination, False):
                        os.remove(obj.destination)
                self._download_item(item)
