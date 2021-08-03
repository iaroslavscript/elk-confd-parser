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
    arg_parser.add_argument("--debug-c")
    arg_parser.add_argument("--debug-i")

    opts = arg_parser.parse_args(args)

    opts.debug_c = opts.debug_c.split(',') if opts.debug_c is not None else []
    opts.debug_i = opts.debug_i.split(',') if opts.debug_i is not None else []

    with open(opts.filename) as f:  # TODO check file exists; check permittions

        text = f.read()
        parser.parse(text, opts.debug_c, opts.debug_i)


if __name__ == "__main__":  # noqa
    main(sys.argv[1:])
