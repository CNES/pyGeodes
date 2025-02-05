"""This script takes a geodes data model XML file as an input and generates a simplified JSON at pygeodes/data/model.json, to provide a summary of all requestable args"""

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup


def parse(filename: str):
    with open(filename, "r") as file:
        content = file.read()

    parser = BeautifulSoup(content, features="xml")
    model = parser.find("model")

    output = {"version": model.find("version").text, "attributes": []}

    for attribute in model.find_all(
        "attribute", {"indexed": True}, recursive=False
    ):  # attributes which don't belong to any fragment
        attr_type = attribute.find("type").text
        output["attributes"].append(
            f'{attribute.find("name").text} ({attr_type})'
        )

    for fragment in model.find_all("fragment"):
        frag_name = fragment.find("name").text
        for attribute in fragment.find_all("attribute", {"indexed": True}):
            attr_name = attribute.find("name").text
            attr_type = attribute.find("type").text
            output["attributes"].append(
                f"{frag_name}:{attr_name} ({attr_type})"
            )

    path = (
        Path(__file__)
        .resolve()
        .parent.parent.joinpath("pygeodes")
        .joinpath("data")
        .joinpath("model.json")
    )

    with open(path, "w") as file:
        json.dump(output, file, indent=4)

    print(f"Model outputed to {str(path)}")


if __name__ == "__main__":
    if len(sys.argv) == 0:
        print(f"Please provide an XML data model file to parse")
        sys.exit(1)

    filename = sys.argv[1]
    parse(filename)
