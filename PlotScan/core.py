"""
Module bundling all functions needed to digitise a scientific plot
"""
import sys
import os
import typing as T
from pathlib import Path
import logging
import numpy as np
import numpy.polynomial.polynomial as poly
import cv2 as cv
from PlotScan import grid
from PlotScan import geometry
from .trajectory import find_trajectory, normalize
from .points import find_points

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)
ix_, iy_ = 0, 0
params_: T.Dict[str, T.Any] = {}
args_: T.Optional[T.Any] = None
# NOTE: remember these are cv coordinates and not numpy.
locations_: T.List[geometry.Point] = []
points_: T.List[geometry.Point] = []
img_: np.ndarray = np.zeros((1, 1))


def plot_traj(traj, outfile: Path):
    """
    Plot the trajectory and save the plot to a file.

    Parameters:
        traj (list): The trajectory to be plotted in the format [(x1, y1), (x2, y2), ...].
        outfile (Path): The path to save the plot.

    Returns:
        None.
    """
    import matplotlib.pyplot as plt

    x, y = zip(*traj)
    plt.figure()
    plt.subplot(211)
    for location in locations_:
        csize = img_.shape[0] // 40
        cv.circle(img_, (location.x, img_.shape[0] - location.y), csize, 128, -1)
    plt.imshow(img_, interpolation="none", cmap="gray")
    plt.axis(False)
    plt.title("Original")
    plt.subplot(212)
    plt.title("Reconstructed")
    plt.plot(x, y)
    plt.tight_layout()
    if not str(outfile):
        plt.show()
    else:
        plt.savefig(outfile)
        logging.info(f"Saved to {outfile}")
    plt.close()


def list_to_points(points) -> T.List[geometry.Point]:
    """
    Convert a list of points to a list of geometry.Point objects.

    Parameters:
        points (list): List of points in the format [(x1, y1), (x2, y2), ...].

    Returns:
        list: A list of geometry.Point objects.
    """
    return [geometry.Point.convert(point) for point in points]


def axis_transformation(p, P: T.List[geometry.Point]):
    """
    Compute the transformation parameters (slope and offset) to transform one axis (X) to another (Y).

    Parameters:
        p (list): The list of points on axis X in the format [(x1, y1), (x2, y2), ...].
        P (list): The list of points on axis Y in the format [(x1, y1), (x2, y2), ...].

    Returns:
        tuple: Two tuples containing the slope (sX, sY) and offset (offX, offY) for the X and Y axes.
    """
    # Currently only linear maps and only 2D.
    px, py = zip(*p)
    Px, Py = zip(*P)
    offX, sX = poly.polyfit(px, Px, 1)
    offY, sY = poly.polyfit(py, Py, 1)
    return (sX, sY), (offX, offY)


def transform_axis(img, erase_near_axis: int = 0):
    """
    Transform the axis of the image.

    Parameters:
        img (numpy.ndarray): The image to be transformed.
        erase_near_axis (int, optional): The number of extra rows and columns to erase near the axis. Default is 0.

    Returns:
        tuple: Two tuples containing the slope (sX, sY) and offset (offX, offY) for the transformed X and Y axes.
    """
    # extra: extra rows and cols to erase. Help in containing error near axis.
    # compute the transformation between old and new axis.
    T = axis_transformation(points_, locations_)
    p = geometry.find_origin(locations_)
    offCols, offRows = p.x, p.y
    logging.info(f"{locations_} → origin {offCols}, {offRows}")
    img[:, : offCols + erase_near_axis] = params_["background"]
    img[-offRows - erase_near_axis:, :] = params_["background"]
    logging.debug(f"Tranformation params: {T}")
    return T


def _find_trajectory_colors(
        img: np.ndarray, plot: bool = False
) -> T.Tuple[int, T.List[int]]:
    """
    Find the colors corresponding to the trajectories in the image.

    Parameters:
        img (numpy.ndarray): The image.
        plot (bool, optional): Whether to plot the histogram. Default is False.

    Returns:
        tuple: The background color and a list of trajectory colors.
    """

    # Each trajectory color x is bounded in the range x-3 to x+2 (interval of
    # 5) -> total 51 bins. Also, it is very unlikely that colors which are too
    # close to each other are part of different trajecotries. It is safe to
    # assme a binwidth of at least 10px.
    hs, bs = np.histogram(img.flatten(), 255 // 10, (0, img.max()))

    # Now a trajectory is only trajectory if number of pixels close to the
    # width of the image (we are using at least 75% of width).
    hs[hs < img.shape[1] * 3 // 4] = 0

    if plot:
        import matplotlib.pyplot as plt

        plt.figure()
        plt.bar(bs[:-1], np.log(hs))
        plt.xlabel("color")
        plt.ylabel("log(#pixel)")
        plt.show()

    # background is usually the color which is most count. We can find it
    # easily by sorting the histogram.
    hist = sorted(zip(hs, bs), reverse=True)

    # background is the most occuring pixel value.
    bgcolor = int(hist[0][1])

    # we assume that bgcolor is close to white.
    if bgcolor < 128:
        logging.error(
            "I computed that background is 'dark' which is unacceptable to me."
        )
        sys.exit()

    # If the background is white, search from the trajectories from the black.
    trajcolors = [int(b) for h, b in hist if h > 0 and b / bgcolor < 0.5]
    return bgcolor, trajcolors


def compute_foregrond_background_stats(img) -> T.Dict[str, float]:
    """
    Compute the foreground and background colors of the image.

    Parameters:
        img (numpy.ndarray): The image.

    Returns:
        dict: A dictionary containing the computed foreground and background colors.
    """
    params: T.Dict[str, T.Any] = {}
    # Compute the histogram. It should be a multimodal histogram. Find peaks
    # and these are the colors of background and foregorunds. Currently,
    # implementation is very simple.
    bgcolor, trajcolors = _find_trajectory_colors(img)
    params["background"] = bgcolor
    params["timeseries_colors"] = trajcolors
    logging.debug(f" computed parameters: {params}")
    return params


def process_image(img):
    """
    Process the image to extract trajectories.

    Parameters:
        img (numpy.ndarray): The image.

    Returns:
        list: The extracted trajectory in the format [(x1, y1), (x2, y2), ...].
    """
    params_ = compute_foregrond_background_stats(img)

    T = transform_axis(img, erase_near_axis=3)
    assert img.std() > 0.0, "No data in the image!"
    logging.info(f" {img.mean()}  {img.std()}")

    # extract the plot that has color which is farthest from the background.
    trajcolor = params_["timeseries_colors"][0]
    img = normalize(img)
    traj, img = find_trajectory(img, trajcolor, T)
    return traj


def run(args):
    """
    Main function to run the trajectory extraction process.

    Parameters:
        args: Command-line arguments.

    Returns:
        None.
    """
    global img_, args_
    args_ = args

    infile = Path(args.INPUT)
    assert infile.exists(), f"{infile} does not exists."
    logging.info(f"Extracting trajectories from {infile}")

    # reads into gray-scale.
    img_ = cv.imread(str(infile), 0)
    img_ = normalize(img_)

    # erosion after dilation (closes gaps)
    if args_.preprocess:
        kernel = np.ones((1, 1), np.uint8)
        img_ = cv.morphologyEx(img_, cv.MORPH_CLOSE, kernel)

    # remove grids.
    img_ = grid.remove_grid(img_)

    # rescale it again.
    img_ = normalize(img_)
    logging.debug(" {img_.min()=} {img_.max()=}")
    assert img_.max() <= 255
    assert img_.min() < img_.mean() < img_.max(), "Could not read meaningful data"
    if args.data_point:
        points_ = list_to_points(args.data_point)
    else:
        points = find_points(infile)
        points_ = list_to_points([point[1] for point in points])
    if args.location:
        locations_ = list_to_points(args.location)
    else:
        points = find_points(infile)
        locations_ = list_to_points([point[0] for point in points])
    # logging.debug(f"data points {args.data_point} → location on image {args.location}")

    traj = process_image(img_)
    if args_.plot:
        plot_traj(traj, args_.plot)
    outfile = args.output or f"{args.INPUT}.traj.csv"
    with open(outfile, "w", encoding="utf-8") as file:
        for r in traj:
            file.write("%g %g\n" % r)
    logging.info(f"Wrote trajectory to {outfile}")
