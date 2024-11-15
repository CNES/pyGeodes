"""This scripts copies project metadata from pyproject.toml file into a pygeodes/_info to provide info about the lib in the CLI"""

import toml
from pathlib import Path

pyproject = Path(__file__).resolve().parent.parent.joinpath("pyproject.toml")

with open(str(pyproject), "r") as f:
    data = toml.loads(f.read())

poetry = data.get("tool").get("poetry")
info_file = (
    Path(__file__)
    .resolve()
    .parent.parent.joinpath("pygeodes")
    .joinpath("_info.py")
)

with open(info_file, "w") as file:
    text = f"""version = "{poetry.get('version')}"
name = "{poetry.get('name')}"
description = "{poetry.get('description')}"
author = "{', '.join(poetry.get('authors'))}"
"""
    file.write(text)
