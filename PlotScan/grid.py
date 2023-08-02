"""
Grid module for removing grid lines from an image.

This module provides functions to remove grid lines from an image. The `remove_horizontal_grid_simple` function removes
horizontal grid lines from the image based on the mean and standard deviation of the pixel values in each row. The
`heal` function performs a morphological operation to heal the image by removing small grid artifacts.

Functions:
    remove_horizontal_grid_simple(img: np.ndarray) -> np.ndarray:
        Remove horizontal grid lines from the image based on the mean and standard deviation of pixel values in each
        row.

    heal(orig: np.ndarray) -> np.ndarray:
        Perform a morphological operation to heal the image and remove small grid artifacts.

    remove_grid(orig: np.ndarray, num_iter: int = 3, background_color: int = 255, grid_size: int = 2) -> np.ndarray:
        Remove grid lines from the image using a combination of morphological operations.

    test_remove_grid(imgfile: Path, debug: bool = True):
        Test function to demonstrate grid removal on an image.

Usage:
    from .grid import remove_horizontal_grid_simple, heal, remove_grid, test_remove_grid

    # Load the image using OpenCV
    img = cv.imread("image.png", 0)

    # Remove horizontal grid lines using the simple method
    without_horizontal_grid = remove_horizontal_grid_simple(img)

    # Heal the image to remove small grid artifacts
    healed_img = heal(img)

    # Remove grid lines using the morphological operation
    without_grid = remove_grid(img)

    # Test grid removal on an image and save the results
    test_remove_grid("image.png", debug=True)
"""
import cv2 as cv
import numpy as np


def _save_fig(img, outfile):
    """
    Save the image to the specified output file.

    Parameters:
        img (np.ndarray): The image to be saved as a NumPy array representing grayscale image data.
        outfile (str): The path to the output file where the image will be saved.
    """
    print(f"Saved to {outfile}")
    cv.imwrite(outfile, img)


def remove_horizontal_grid_simple(img) -> np.ndarray:
    """
    Remove horizontal grid lines from the image based on the mean and standard deviation of pixel values in each row.

    Parameters:
        img (np.ndarray): The input image as a NumPy array representing grayscale image data.

    Returns:
        np.ndarray: The image after removing horizontal grid lines as a NumPy array representing grayscale image data.
    """
    mu, sigma = img.mean(), img.std()
    for i, row in enumerate(img):
        if row.mean() < mu - sigma:
            # I can simply remove the row.
            img[i, :] = img.max()
    return img


def heal(orig):
    """
    Perform a morphological operation to heal the image and remove small grid artifacts.

    Parameters:
        orig (np.ndarray): The original image as a NumPy array representing grayscale image data.

    Returns:
        np.ndarray: The healed image as a NumPy array representing grayscale image data.
    """
    kernel = np.ones((3, 3), np.uint8)
    return cv.morphologyEx(orig.copy(), cv.MORPH_OPEN, kernel, iterations=2)


def remove_grid(
    orig, num_iter=3, background_color: int = 255, grid_size: int = 2
) -> np.ndarray:
    """
    Remove grid lines from the image using a combination of morphological operations.

    Parameters:
        orig (np.ndarray): The original image as a NumPy array representing grayscale image data.
        num_iter (int, optional): The number of iterations to be used for the morphological operation (default is 3).
        background_color (int, optional): The color value to be used for the background after removing the grid lines
                                          (default is 255).
        grid_size (int, optional): The thickness of grid lines to be removed (default is 2).

    Returns:
        np.ndarray: The image after removing grid lines as a NumPy array representing grayscale image data.
    """
    img = orig.copy()
    thres = cv.threshold(img, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    # Remove horizontal lines
    horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (40, 1))
    remove_horizontal = cv.morphologyEx(
        thres, cv.MORPH_OPEN, horizontal_kernel, iterations=num_iter
    )
    cnts = cv.findContours(remove_horizontal, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for cnt in cnts:
        cv.drawContours(img, [cnt], -1, background_color, grid_size)

    # Remove vertical lines
    vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 40))
    remove_vertical = cv.morphologyEx(
        thres, cv.MORPH_OPEN, vertical_kernel, iterations=num_iter
    )
    cnts = cv.findContours(remove_vertical, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for cnt in cnts:
        cv.drawContours(img, [cnt], -1, background_color, grid_size)
    return img
