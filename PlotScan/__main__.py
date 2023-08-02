"""
PlotScan terminal client
"""
import argparse
from pathlib import Path
from .core import run


def main():
    """Main function"""
    description = """A command-line tool for extracting data from scientific figure images."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "INPUT",
        type=Path,
        help="Path to the input image file.",
    )
    parser.add_argument(
        "--pixel-tolerance",
        "-tol",
        required=False,
        default=1,
        type=int,
        help="The maximum allowable difference in pixel coordinates. Default is 1.",
    )
    parser.add_argument(
        "--data-point",
        "-p",
        required=False,
        default=None,
        action="append",
        help="Data points to define axes in the format x0,y0 -p x1,y1 -p x2,y2. "
             "The first point defines the origin and at least 2 more points are "
             "required to define the axes. "
             "Make sure that points are comma-separated without any space.",
    )
    parser.add_argument(
        "--location",
        "-l",
        required=False,
        default=None,
        action="append",
        type=int,
        help="Location of the points on the figure in pixels (integer). "
             "These values should appear in the same order as the -p option.",
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
        help="Name of the output file. If not provided, the trajectory will be written to "
             " <INPUT>.traj.csv",
    )
    parser.add_argument(
        "--preprocess",
        required=False,
        action="store_true",
        help="Preprocess the image. Useful for improving bad resolution images.",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
