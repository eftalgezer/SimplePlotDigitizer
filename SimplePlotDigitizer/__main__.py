import argparse
from .core import run

def main():
    # Argument parser.

    description = """Digitize image."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("INPUT", type=Path, help="Input image file.")
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
