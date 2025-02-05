#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module provides tools to make synchronous and asynchronous HTTP requests
"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

import asyncio
import json
import time
import warnings
from time import perf_counter

# stdlib imports -------------------------------------------------------
from typing import Any, Dict, List
from urllib.parse import urljoin

import aiofiles
import aiohttp
import remotezip

# third-party imports -----------------------------------------------
import requests
import validators
from requests.adapters import HTTPAdapter, Retry
from tqdm import tqdm
from tqdm.asyncio import tqdm as tqdm_async

from pygeodes.utils.consts import (
    DOWNLOAD_CHUNK_SIZE,
    MAX_CONCURRENT_DOWNLOADS,
    MAX_NB_RETRIES,
    MAX_PAGE_SIZE,
    REQUESTS_TIMEOUT,
    SSL_CERT_PATH,
    TIME_BEFORE_RETRY,
)
from pygeodes.utils.decorators import uses_session
from pygeodes.utils.exceptions import InvalidChecksumException
from pygeodes.utils.io import (
    check_if_folder_already_contains_file,
    compute_md5,
    file_exists,
    find_unused_filename,
)

# local imports ---------------------------------------------------
from pygeodes.utils.logger import logger
from pygeodes.utils.profile import (
    Download,
    Profile,
    load_profile_and_save_download,
)


def make_params(
    page: int,
    query: dict,
    bbox: List[float] = None,
    intersects: dict = None,
    collections: List[str] = None,
):
    return {
        "page": page,
        "query": query,
        "limit": MAX_PAGE_SIZE,
        "bbox": bbox,
        "intersects": intersects,
        "collections": collections,
    }


def valid_url(url: str) -> bool:
    return validators.url(url)


def auth_headers(api_key: str):
    if api_key is None:
        return {}
    else:
        return {"X-API-Key": api_key}


def check_all_different(objects):
    ids = [obj.id for obj in objects]
    unique = set(ids)
    return len(unique) == len(ids)


class RequestMaker:
    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url
        self.api_key = api_key
        self.authorization_headers = auth_headers(self.api_key)
        self.get_headers = self.authorization_headers
        self.post_headers = {
            **self.authorization_headers,
            "Content-type": "application/json",
        }
        if file_exists(SSL_CERT_PATH, False):
            self.verify = SSL_CERT_PATH
            logger.debug(f"using ssl certif from {SSL_CERT_PATH}")
        else:
            self.verify = False
            logger.debug("using without ssl certif")

    def get_full_url(self, endpoint: str) -> str:
        if not endpoint.startswith("http"):
            return urljoin(self.base_url, endpoint)
        else:
            return endpoint


class SyncRequestMaker(RequestMaker):
    def open_session(self):
        retries = Retry(
            total=MAX_NB_RETRIES,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def close_session(self):
        self.session.close()

    @uses_session
    def download_file(
        self,
        endpoint: str,
        outfile: str,
        checksum: str,
        checksum_error: bool = True,
        verbose: bool = True,
    ):
        url = self.get_full_url(endpoint)
        outfile = find_unused_filename(outfile)

        name_for_same_file = check_if_folder_already_contains_file(
            outfile, checksum
        )

        if name_for_same_file is not None:
            warnings.warn(
                f"trying to download content at {outfile} but file with same content already exists in the same folder at {name_for_same_file}, skipping download"
            )
            return name_for_same_file

        with self.session.get(
            url,
            stream=True,
            verify=self.verify,
            headers=self.get_headers,
        ) as r:
            logger.debug(f"Download at {url} started")
            r.raise_for_status()

            if r.status_code == 429:
                raise Exception(
                    f"Too many requests, your request quota is empty"
                )

            total_size = int(r.headers.get("content-length", 0))

            with open(outfile, "wb") as f:
                with tqdm(
                    leave=False,
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"downloading file",
                    initial=0,
                    disable=not verbose,
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                        f.write(chunk)
                        pbar.update(len(chunk))

            logger.debug(f"Download at {url} ended")

        md5 = compute_md5(outfile)
        logger.debug(f"Checking checksum of {outfile} : {checksum} == {md5} ?")

        if checksum != md5:
            message = f"MD5 Checksum for file {outfile} couldn't be verified"
            if checksum_error:
                raise InvalidChecksumException(message)
            else:
                logger.error(message)

        logger.debug(f"Download completed at {outfile}")
        if verbose:
            print(f"Download completed at {outfile}")
        return outfile

    @uses_session
    def get(
        self,
        endpoint: str,
        headers: Dict[str, str] = None,
    ) -> Any:

        url = self.get_full_url(endpoint)
        logger.debug(f"making GET request to {url}")

        if not headers:
            headers = {}

        for attempt in range(MAX_NB_RETRIES):
            begin = perf_counter()
            response = self.session.get(
                url,
                headers={**headers, **self.authorization_headers},
                stream=True,
                timeout=REQUESTS_TIMEOUT,
                verify=self.verify,
            )
            end = perf_counter()
            logger.debug(f"request made in {end-begin} seconds")
            if response.ok:
                return response

            if response.status_code == 429:
                raise Exception(
                    f"Too many requests, your request quota is empty"
                )

            if attempt == MAX_NB_RETRIES - 1:
                response.raise_for_status()
            if response.reason == "Forbidden":
                raise Exception("Forbidden: Check your api_key")

            if attempt > 0:
                logger.warning("Attempt %s of %s", attempt + 1, MAX_NB_RETRIES)

            logger.debug("Waiting %s seconds", TIME_BEFORE_RETRY)
            time.sleep(TIME_BEFORE_RETRY)
        return None

    @uses_session
    def post(
        self,
        endpoint: str,
        data: Dict[str, str],
        headers: Dict[str, str] = None,
    ) -> Any:

        url = self.get_full_url(endpoint)

        if not headers:
            headers = {}

        full_headers = {**headers, **self.post_headers}
        logger.debug(
            f"making POST request to {url} with headers = {full_headers} and {data=}"
        )

        for attempt in range(MAX_NB_RETRIES):
            begin = perf_counter()
            response = self.session.post(
                url,
                headers=full_headers,
                stream=True,
                timeout=REQUESTS_TIMEOUT,
                data=json.dumps(data),
                verify=self.verify,
            )
            end = perf_counter()
            logger.debug(f"request made in {end-begin} seconds")

            if response.ok:
                return response

            if response.status_code == 429:
                raise Exception(
                    f"Too many requests, your request quota is empty"
                )

            if attempt == MAX_NB_RETRIES - 1:
                response.raise_for_status()
            if response.reason == "Forbidden":
                raise Exception("Forbidden: Check your api_key")

            if attempt > 0:
                logger.warning("Attempt %s of %s", attempt + 1, MAX_NB_RETRIES)

            logger.debug("Waiting %s seconds", TIME_BEFORE_RETRY)
            time.sleep(TIME_BEFORE_RETRY)
        return None

    @uses_session
    def list_files_in_archive(self, archive_url: str) -> List[str]:
        logger.debug(f"Starting to list files for {archive_url}")
        files = []

        with remotezip.RemoteZip(
            archive_url,
            session=self.session,
            verify=self.verify,
            headers=self.authorization_headers,
        ) as zip:
            for zip_info in zip.infolist():
                files.append(zip_info.filename)

        logger.debug(f"Ending to list files for {archive_url}")
        return files

    @uses_session
    def extract_file_from_archive(
        self, archive_url: str, filename: str, download_dir: str
    ):

        logger.debug(
            f"Downloading file {filename} from archive {archive_url} in {download_dir}"
        )
        with remotezip.RemoteZip(
            archive_url,
            session=self.session,
            verify=self.verify,
            headers=self.authorization_headers,
        ) as zip:
            zip.extract(filename, download_dir)
        logger.debug("Download ended")


class AsyncRequestMaker(RequestMaker):

    def download_files(
        self,
        endpoints: List[str],
        outfiles: str,
        checksums: str,
        checksum_error: bool = True,
    ):
        if len(endpoints) != len(outfiles):
            raise Exception(
                f"endpoints ({len(endpoints)}) and outfiles ({len(outfiles)}) must have the same lengths"
            )

        asyncio.run(
            self.download_files_async(endpoints=endpoints, outfiles=outfiles)
        )
        for outfile, checksum in zip(outfiles, checksums):
            md5 = compute_md5(outfile)
            logger.debug(
                f"Checking checksum of {outfile} : {checksum} == {md5} ?"
            )

            if checksum != md5:
                message = (
                    f"MD5 Checksum for file {outfile} couldn't be verified"
                )
                if checksum_error:
                    raise InvalidChecksumException(message)
                else:
                    logger.error(message)

            logger.debug(f"Download completed at {outfile}")

    async def download_files_async(self, endpoints: List[str], outfiles: str):

        sem = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

        async def fetch(
            session: aiohttp.ClientSession,
            endpoint: str,
            outfile: str,
        ):

            url = self.get_full_url(endpoint)

            download_for_profile = Download(url=url, destination=outfile)
            download_for_profile.start()
            load_profile_and_save_download(download_for_profile)

            async with sem:

                async with session.get(
                    url,
                    headers={**self.get_headers},
                    ssl=False,
                ) as response:

                    if response.status == 200:
                        async with aiofiles.open(outfile, "wb") as f:
                            async for chunk in response.content.iter_chunked(
                                DOWNLOAD_CHUNK_SIZE
                            ):
                                await f.write(chunk)

                        profile = Profile.load()

                        download_for_profile = profile.get_download_from_uuid(
                            download_for_profile._id
                        )
                        download_for_profile.complete()

                        profile.save()

        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.ensure_future(fetch(session, endpoint, outfile))
                for endpoint, outfile in zip(endpoints, outfiles)
            ]
            await tqdm_async.gather(*tasks, total=len(endpoints))

        await asyncio.sleep(0.1)

    def get(self, endpoints: List[str], headers: List[Dict[str, str]] = None):
        if headers is None:
            headers = [None for _ in range(len(endpoints))]

        responses = asyncio.run(
            self.get_async(endpoints=endpoints, headers=headers)
        )
        return responses

    def post(
        self,
        endpoints: List[str],
        datas: List[Dict],
        headers: List[Dict[str, str]] = None,
    ):
        if len(endpoints) != len(datas):
            raise Exception(
                f"endpoints ({len(endpoints)}) and datas ({len(datas)}) must have the same lengths"
            )

        if headers is None:
            headers = [None for _ in range(len(endpoints))]

        logger.debug(f"starting {len(endpoints)} async post requests")

        responses = asyncio.run(
            self.post_async(endpoints=endpoints, headers=headers, datas=datas)
        )
        return responses

    async def control(self, response: aiohttp.ClientResponse):
        if not response.ok:
            raise ConnectionError(
                f"Couldn't make request to {response.url} ({response.status} - {response.reason})"
            )
        else:
            return await response.json()

    async def post_async(
        self,
        endpoints: List[str],
        headers: List[Dict[str, str]],
        datas: List[Dict],
    ):

        async def fetch(
            session: aiohttp.ClientSession,
            endpoint: str,
            headers: Dict[str, str],
            data: Dict,
        ):
            if headers is None:
                headers = {}

            logger.debug(
                f"making async post request to {endpoint} with {data=}"
            )
            async with session.post(
                self.get_full_url(endpoint),
                headers={**headers, **self.post_headers},
                data=json.dumps(data),
                ssl=False,
            ) as response:

                return await self.control(response)

        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.ensure_future(fetch(session, endpoint, _headers, data))
                for endpoint, _headers, data in zip(endpoints, headers, datas)
            ]
            responses = await tqdm_async.gather(*tasks, total=len(endpoints))

        await asyncio.sleep(0.2)

        return responses

    async def get_async(
        self, endpoints: List[str], headers: List[Dict[str, str]]
    ):

        async def fetch(
            session: aiohttp.ClientSession,
            endpoint: str,
            headers: Dict[str, str],
        ):
            if headers is None:
                headers = {}

            async with session.get(
                self.get_full_url(endpoint),
                headers={**headers, **self.get_headers},
            ) as response:
                return await self.control(response)

        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.ensure_future(fetch(session, endpoint, _headers))
                for endpoint, _headers in zip(endpoints, headers)
            ]
            responses = await tqdm_async.gather(*tasks, total=len(endpoints))

        await asyncio.sleep(0.2)

        return responses
