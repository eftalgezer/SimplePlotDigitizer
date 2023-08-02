"""
Geometry module for handling 2D points and computing the origin of given points.

This module provides a Point class to represent 2D points with x and y coordinates. It also includes a function
`find_origin` to compute the origin of a set of points based on their colinearity.

Classes:
    Point: A class representing 2D points with x and y coordinates.

Functions:
    find_origin(points: List[Point]) -> Point:
        Compute the origin of given points based on their colinearity.

Usage:
    from .geometry import Point, find_origin

    # Creating Point objects
    point1 = Point(10, 20)
    point2 = Point(30, 40)

    # Converting a coordinate representation to a Point object
    coords = "50, 60"
    p3 = Point.convert(coords)  # Result: Point(50, 60)

    # Computing the origin of points
    points = [Point(10, 20), Point(30, 40), Point(50, 60)]
    origin = find_origin(points)  # Result: Point(10, 20)

Note:
    - The Point class provides methods for comparison, hashing, and string representation.
    - The find_origin function finds the colinear points from the given list of points and computes the origin as the
      average of the vertical and horizontal points.
"""
import typing as T
import statistics
import math


class Point:
    """
    Represents a 2D point with x and y coordinates.

    Attributes:
        x (int): The x-coordinate of the point.
        y (int): The y-coordinate of the point.

    Methods:
        __init__(self, x: int, y: int):
            Initializes a Point object with the given x and y coordinates.

        convert(cls, coords) -> Point:
            Converts a coordinate representation to a Point object.

        __eq__(self, other) -> bool:
            Checks if two Point objects are equal.

        __hash__(self):
            Computes the hash value for the Point object.

        __repr__(self) -> str:
            Returns a string representation of the Point object.

        __iter__(self) -> iterator:
            Returns an iterator for the Point object containing x and y coordinates.
    """
    def __init__(self, x, y):
        """
        Initialize a Point object with x and y coordinates.

        Parameters:
            x (float): The x-coordinate of the point.
            y (float): The y-coordinate of the point.

        Returns:
            None.
        """
        self.x = int(x)
        self.y = int(y)

    @classmethod
    def convert(cls, coords) -> "Point":
        """
        Convert a coordinate representation to a Point object.

        Parameters:
            coords (Union[str, List[float]]): The coordinate representation. It can be a string in the format "x,y"
                                             or a list of two floats representing (x, y) coordinates.

        Returns:
            Point: The Point object created from the coordinates.
        """
        if isinstance(coords, str):
            xy = [float(coord) for coord in coords.split(",")]
        else:
            xy = [float(coord) for coord in coords]
        return cls(xy[0], xy[1])

    def __eq__(self, other) -> bool:
        """
        Check if two Point objects are equal.

        Parameters:
            other (Point): The other Point object to compare with.

        Returns:
            bool: True if the two points are equal, False otherwise.
        """
        return (self.x == other.x) and (self.y == other.y)

    def __hash__(self):
        """
        Compute the hash value for the Point object.

        Returns:
            int: The hash value.
        """
        return hash((self.x, self.y))

    def __repr__(self):
        """
        Get a string representation of the Point object.

        Returns:
            str: A string representation of the Point object in the format "(x, y)".
        """
        return f"({self.x}, {self.y})"

    def __iter__(self):
        """
        Return an iterator for the Point object.

        Returns:
            iterator: An iterator containing the x and y coordinates of the point.
        """
        return iter((self.x, self.y))


def find_origin(points: T.List[Point]) -> Point:
    """
    Compute the origin of given points.

    Parameters:
        points (List[Point]): A list of Point objects representing the points.

    Returns:
        Point: The Point object representing the origin.
    """
    horizontal = set()
    for i, point1 in enumerate(points):
        for point2 in points[i + 1:]:
            if abs(point1.x - point2.x) <= 2:
                continue
            m = (point2.y - point1.y) / (point2.x - point1.x)
            if abs(m) < math.tan(math.pi / 180 * 5):  # <5 deg is horizontal.
                horizontal.add(point1)
                horizontal.add(point2)

    points = set(points)
    assert len(horizontal) > 1, f"Must have at least two colinear points {horizontal}"
    verticals = points - horizontal
    assert len(verticals) > 0, "Must be at least one vertical point"
    origin_y = statistics.mean([point.y for point in horizontal])
    origin_x = statistics.mean([point.x for point in verticals])
    return Point(origin_x, origin_y)
