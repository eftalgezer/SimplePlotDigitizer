__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import sys
import subprocess
import numpy as np
from pathlib import Path

import SimplePlotDigitizer

HERE = Path(__file__).parent.resolve()


def _run_cmdline(infile: Path,):
    cmd = f"python -m SimplePlotDigitizer {str(infile)} "
    cmd += f"{pts} {locs}"
    outfile = infile.with_suffix(".result.png")
    trajfile = infile.with_suffix(".result.csv")
    cmd += f" --plot {str(outfile)} --output {trajfile}"
    r = subprocess.run(cmd, check=True, shell=True)
    assert r.returncode == 0, f"Failed test {r.returncode}"
    return trajfile


def _check_csv_file(csvfile):
    data = np.loadtxt(csvfile)
    y = data[:, 1]
    assert y.std() > 0.0
    assert y.min() < y.mean() < y.max()


def test_trimmeed():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "trimmed.png"
    )
    _check_csv_file(csvfile)


def test_graph1():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "graphs_1.png"
    )
    _check_csv_file(csvfile)


def test_ecg():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "ECGImage.png"
    )
    _check_csv_file(csvfile)


def test_grid():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "graph_with_grid.png"
    )
    _check_csv_file(csvfile)
