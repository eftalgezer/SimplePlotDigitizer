"""
Test module for testing the command-line interface (CLI) of the main application.

This module contains test cases to validate the command-line interface (CLI) of the main application. It checks if
the application can be executed with the expected command-line arguments and options.

Functions:
    test_trimmed():
        Test if the application can process the 'trimmed.png' image and generate a trajectory file.

    test_graph1(): Test if the application can process the 'graphs_1.png' image with custom data points and locations
    and generate a trajectory file.

    test_ecg(): Test if the application can process the 'ECGImage.png' image with custom data points and locations
    and generate a trajectory file.

    test_grid():
        Test if the application can process the 'graph_with_grid.png' image and generate a trajectory file.

    _run_cmdline(infile: Path, points=None, locations=None) -> Path: Helper function to run the PlotScan application
    with specified input file, data points, and locations. Returns the path of the generated trajectory file.

    _check_csv_file(csvfile: Path):
        Helper function to check the validity of the generated CSV trajectory file.
"""

import subprocess
from pathlib import Path
import numpy as np
import PlotScan

HERE = Path(__file__).parent.resolve()


def _run_cmdline(infile: Path, points=None, locations=None):
    """
    Run the PlotScan application with the specified input file, data points, and locations.

    Parameters:
        infile (Path): The input file to be processed.
        points (list, optional): List of custom data points. Defaults to None.
        locations (list, optional): List of custom locations on the image. Defaults to None.

    Returns:
        Path: The path of the generated trajectory file.
    """
    pts = None
    locs = None
    cmd = f"PlotScan {str(infile)} "
    if points:
        pts = " ".join([f"-p {','.join(map(str,pt))}" for pt in points])
    if locations:
        locs = " ".join([f"-l {','.join(map(str,pt))}" for pt in locations])
    if points and locations:
        cmd += f"{pts} {locs}"
    outfile = infile.with_suffix(".result.png")
    trajfile = infile.with_suffix(".result.csv")
    cmd += f" --plot {str(outfile)} --output {trajfile}"
    r = subprocess.run(cmd, check=True, shell=True)
    assert r.returncode == 0, f"Failed test {r.returncode}"
    return trajfile


def _check_csv_file(csvfile):
    """
    Check the validity of the generated CSV trajectory file.

    Parameters:
        csvfile (Path): The path of the generated CSV trajectory file.
    """
    data = np.loadtxt(csvfile)
    y = data[:, 1]
    assert y.std() > 0.0
    assert y.min() < y.mean() < y.max()


def test_trimmeed():
    """Test if the application can process the 'trimmed.png' image and generate a trajectory file."""
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "trimmed.png"
    )
    _check_csv_file(csvfile)


def test_graph1():
    """
    Test if the application can process the 'graphs_1.png' image with custom data points and locations and generate a
    trajectory file.
    """
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "graphs_1.png",
        [(1, 0), (6, 0), (0, 3)],
        [(165, 52), (599, 51), (85, 151)],
    )
    _check_csv_file(csvfile)


def test_ecg():
    """
    Test if the application can process the 'ECGImage.png' image with custom data points and locations and generate a
    trajectory file.
    """
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "ECGImage.png",
        [(1, 0), (5, 0), (0, 1)],
        [(290, 44), (1306, 43), (106, 301)],
    )
    _check_csv_file(csvfile)


def test_grid():
    """Test if the application can process the 'graph_with_grid.png' image and generate a trajectory file."""
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "graph_with_grid.png"
    )
    _check_csv_file(csvfile)
