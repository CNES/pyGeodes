#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains all things regarding python dataclasses"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
from dataclasses import fields

# third-party imports -----------------------------------------------

# local imports ---------------------------------------------------


def class_from_args(class_obj, arg_dict: str):
    """Returns an instance of a class from the class object and a dictionnary containing all the args

    Parameters
    ----------
    class_obj : Class
        a class object
    arg_dict : str
        an argument dictionnary

    Returns
    -------
    _type_
        an instance of the class class_obj
    """
    fieldset = {f.name for f in fields(class_obj) if f.init}
    filtered_arg_dict = {k: v for k, v in arg_dict.items() if k in fieldset}
    return class_obj(**filtered_arg_dict)
