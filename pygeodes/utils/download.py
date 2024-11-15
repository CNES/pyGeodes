#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module regroups some things related to downloading"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------

# third-party imports -----------------------------------------------

# local imports ---------------------------------------------------
from pygeodes.utils.consts import GEODES_DEFAULT_URL


def correct_download_tld(url: str) -> str:
    """This function corrects the domain name of a download link when needed

    Parameters
    ----------
    url : str
        the download link to corret

    Returns
    -------
    str
        the download link corrected
    """
    if not url.startswith(GEODES_DEFAULT_URL):  # needs to be corrected
        return url.replace("geodes-portal", "gdh-portal-prod")
    else:
        return url
