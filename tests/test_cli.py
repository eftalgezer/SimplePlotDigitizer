import subprocess
from pathlib import Path
import numpy as np
import PlotScan

HERE = Path(__file__).parent.resolve()


def _run_cmdline(infile: Path, points=None, locations=None):
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
        HERE / ".." / "figures" / "graphs_1.png",
        [(1, 0), (6, 0), (0, 3)],
        [(165, 52), (599, 51), (85, 151)],
    )
    _check_csv_file(csvfile)


def test_ecg():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "ECGImage.png",
        [(1, 0), (5, 0), (0, 1)],
        [(290, 44), (1306, 43), (106, 301)],
    )
    _check_csv_file(csvfile)


def test_grid():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "graph_with_grid.png"
    )
    _check_csv_file(csvfile)
