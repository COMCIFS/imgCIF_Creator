import sys
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from dxtbx.model.experiment_list import ExperimentListFactory

from .core import make_cbf

def parse_commandline(argv):

    description = """\
    Convert a directory of image frames in any format recognised by dxtbx into
    CBF files. The files will be placed in a new directory "CBF" at the same
    level as the directory within which the frames are found.
    """
    ap = ArgumentParser(prog="make_cbf", description=description)
    ap.add_argument(
        "input_dir",
        type=Path,
        nargs='+',
        help="Directory containing files to convert"
    )
    ap.add_argument(
        '--frame-limit',
        type=int,
        default=None,
        help="Convert no more than this many frames."
        )
    args = ap.parse_args(argv)

    return args

def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    args = parse_commandline(argv)

    expts = ExperimentListFactory.from_filenames(args.input_dir)

    make_cbf(expts, frame_limit=args.frame_limit)

if __name__ == '__main__':
    main()
