"""
PlotScan terminal client
"""
import argparse
from pathlib import Path
from .core import run


def main():
    """Main function"""
    description = """Digitize image."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("INPUT", type=Path, help="Input image file.")
    parser.add_argument(
        "--pixel-tolerance",
        "-tol",
        required=False,
        default=1,
        help="The maximum allowable difference in pixel coordinates. Default is 1.",
    )
    parser.add_argument(
        "--data-point",
        "-p",
        required=False,
        default=None,
        action="append",
        help="Datapoints (min 3 required)."
             " At least 3 points are recommended. e.g -p 0,0 -p 10,0 -p 0,1 "
             "Make sure that point are comma separated without any space.",
    )
    parser.add_argument(
        "--location",
        "-l",
        required=False,
        default=None,
        action="append",
        help="Location of a points on figure in pixels (integer)."
             " These values should appear in the same order as -p option.",
    )
    parser.add_argument(
        "--plot",
        default=None,
        required=False,
        help="Plot the final result. Requires matplotlib.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=False,
        type=str,
        help="Name of the output file else trajectory will be written to "
             " <INPUT>.traj.csv",
    )
    parser.add_argument(
        "--preprocess",
        required=False,
        action="store_true",
        help="Preprocess the image. Useful with bad resolution images.",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
