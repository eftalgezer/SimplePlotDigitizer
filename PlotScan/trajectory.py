"""
Module for finding and processing trajectories in an image.

This module provides functions to find and process trajectories in an image. Trajectories are sequences of points
that represent data curves in a plot or graph.

Functions:
    normalize(img: np.ndarray) -> np.ndarray:
        Normalize the pixel values of the image to a range between 0 and 255.

    fit_trajectory_using_median(traj: Dict[int, List[int]], T: Tuple[Tuple[float, float], Tuple[float, float]],
    img: np.ndarray) -> List[Tuple[float, float]]: Fit the trajectory points to the Y = mX + offset model using the
    median method.

    find_trajectory(img: np.ndarray, pixel: int, T: Tuple[Tuple[float, float], Tuple[float, float]]) -> Tuple[List[
    Tuple[float, float]], np.ndarray]: Find the trajectory points of the specified pixel color in the image.

    _valid_px(val: int) -> int:
        Ensure that a pixel value is within the valid range of 0 to 255.

    _find_center(vec: np.ndarray) -> np.float64:
        Find the median of a given vector.

Usage:
    from .trajectory import normalize, fit_trajectory_using_median, find_trajectory

    # Load the image using OpenCV
    img = cv.imread("plot_image.png", 0)

    # Normalize the image
    normalized_img = normalize(img)

    # Define transformation parameters T as (scaling, offset) to convert the pixel coordinates to data coordinates
    T = ((scaling_X, scaling_Y), (offset_X, offset_Y))

    # Find the trajectory points for a specific pixel color
    pixel_color = 128
    trajectory_points, processed_image = find_trajectory(normalized_img, pixel_color, T)

    # Fit the trajectory points using the median method
    fitted_trajectory = fit_trajectory_using_median(trajectory_points, T, processed_image)

    # The fitted_trajectory variable now contains the data points that represent the trajectory in data coordinates.

"""
import logging
from collections import defaultdict
import numpy as np
import cv2 as cv


def _find_center(vec):
    """
    Find the median of a given vector.

    Parameters:
        vec (np.ndarray): The input vector as a NumPy array.

    Returns:
        np.float64: The median value of the input vector.
    """
    return np.median(vec)


# Thanks https://codereview.stackexchange.com/a/185794
def normalize(img):
    """
    Normalize the pixel values of the image to a range between 0 and 255.

    Parameters:
        img (np.ndarray): The input image as a NumPy array.

    Returns:
        np.ndarray: The normalized image as a NumPy array with pixel values ranging from 0 to 255.
    """
    return np.interp(img, (img.min(), img.max()), (0, 255)).astype(np.uint8)


def fit_trajectory_using_median(traj, T, img):
    """
    Fit the trajectory points to the Y = mX + offset model using the median method.

    Parameters: traj (Dict[int, List[int]]): A dictionary containing x-coordinate (int) as keys and corresponding
    list of y-coordinates (List[int]) as values, representing the trajectory points in the image. T (Tuple[Tuple[
    float, float], Tuple[float, float]]): A tuple of two tuples, each containing scaling factors (float) and offsets
    (float) for X and Y axes, respectively. img (np.ndarray): The input image as a NumPy array.

    Returns: List[Tuple[float, float]]: A list of tuples, each containing the fitted data points of the trajectory in
    data coordinates (X, Y).
    """
    (sX, sY), (offX, offY) = T
    res = []
    r, _ = img.shape

    # x, y = zip(*sorted(traj.items()))
    # logging.info((xvec, ys))

    for k in sorted(traj):
        x = k

        vals = np.array(traj[k])

        # For each x, we may multiply pixels in column of the image which might
        # be y. Usually experience is that the trajectories are close to the
        # top rather to the bottom. So we discard call pixel which are below
        # the center of mass (median here)
        # These are opencv pixles. So there valus starts from the top. 0
        # belogs to top row. Therefore > rather than <.
        avg = np.median(vals)
        vals = vals[np.where(vals >= avg)]
        if len(vals) == 0:
            continue

        # Still we have multiple candidates for y for each x.
        # We find the center of these points and call it the y for given x.
        y = _find_center(vals)
        cv.circle(img, (x, int(y)), 1, 255, -1)
        x1 = (x - offX) / sX
        y1 = (r - y - offY) / sY
        res.append((x1, y1))

    # sort by x-axis.
    return sorted(res)


def _valid_px(val: int) -> int:
    """
    Ensure that a pixel value is within the valid range of 0 to 255.

    Parameters:
        val (int): The pixel value to validate.

    Returns:
        int: The pixel value restricted to the range of 0 to 255.
    """
    return min(max(0, val), 255)


def find_trajectory(img: np.ndarray, pixel: int, T):
    """
    Find the trajectory points of the specified pixel color in the image.

    Parameters: img (np.ndarray): The input image as a NumPy array. pixel (int): The pixel color to find the
    trajectory for in the image. T (Tuple[Tuple[float, float], Tuple[float, float]]): A tuple of two tuples,
    each containing scaling factors (float) and offsets (float) for X and Y axes, respectively.

    Returns:
        Tuple[List[Tuple[float, float]], np.ndarray]: A tuple containing:
            - A list of tuples, each containing the found data points of the trajectory in data coordinates (X, Y).
            - The processed image as a NumPy array with additional visualizations for debugging purposes.
    """
    logging.info(f"Extracting trajectory for color {pixel}")
    assert (
        img.min() <= pixel <= img.max()
    ), f"{pixel} is outside the range: [{img.min()}, {img.max()}]"

    # Find all pixels which belongs to a trajectory.
    origin = 6
    _clower, _cupper = _valid_px(pixel - origin // 2), _valid_px(pixel + origin // 2)

    Y, X = np.where((img >= _clower) & (img <= _cupper))
    traj = defaultdict(list)
    for x, y in zip(X, Y):
        traj[x].append(y)

    assert traj, "Empty trajectory"

    # this is a simple fit using median.
    new = np.zeros_like(img)
    res = fit_trajectory_using_median(traj, T, new)
    return res, np.vstack((img, new))
