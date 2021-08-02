#!/bin/env python3

import argparse
import json
import sys
from typing import List

from elkconfdparser import parser
from elkconfdparser import version


def create_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(prog='ELK conf.d parser')
    parser.add_argument('--version', action='version', version=version.__version__)

    return parser


def main(args: List[str]) -> None:

    arg_parser: argparse.ArgumentParser = create_parser()
    arg_parser.add_argument("filename")  # TODO add read from stdin
    opts = arg_parser.parse_args(args)

    with open(opts.filename) as f:  # TODO check file exists; check permittions

        text = f.read()
        #data = parser.parse(text)
        data = parser.parse_by_char(text)

        display(data)


def display(data):

    print(json.dumps(data, indent=4, sort_keys=True))


if __name__ == "__main__":  # noqa
    main(sys.argv[1:])
