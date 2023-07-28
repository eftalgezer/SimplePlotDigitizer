"""
Detect the points from a scientific figure with OCR
"""
import math
from paddleocr import PaddleOCR


def are_rectangles_equal(rect1, rect2, pixel_tolerance=1):
    """
    Check if two rectangles are equal within the given pixel tolerance.

    Parameters:
        rect1 (list): The first rectangle in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        rect2 (list): The second rectangle in the same format as rect1.
        pixel_tolerance (int, optional): The maximum allowable difference in pixel coordinates for the rectangles to be considered equal. Default is 1.

    Returns:
        bool: True if the rectangles are equal within the pixel_tolerance, False otherwise.
    """
    corners1 = rect1[0]
    corners2 = rect2[0]
    if len(corners1) != len(corners2):
        return False
    for i in range(len(corners1)):
        x1, y1 = corners1[i]
        x2, y2 = corners2[i]

        if abs(x1 - x2) > pixel_tolerance or abs(y1 - y2) > pixel_tolerance:
            return False
    return True


def remove_duplicate_rectangles(rectangles, pixel_tolerance=1):
    """
    Remove duplicate rectangles from the list of rectangles.

    Parameters:
        rectangles (list): List of rectangles in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        pixel_tolerance (int, optional): The maximum allowable difference in pixel coordinates for the rectangles to be considered duplicate. Default is 1.

    Returns:
        list: A list of unique rectangles after removing duplicates.
    """
    unique_rectangles = []
    for rect in rectangles:
        is_duplicate = any(
            are_rectangles_equal(rect, unique_rect, pixel_tolerance) for unique_rect in unique_rectangles)

        if not is_duplicate:
            unique_rectangles.append(rect)
    return unique_rectangles


def find_period(points, axis):
    """
    Find the period of the given axis based on the points.

    Parameters:
        points (list): List of points in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        axis (int): The axis to find the period for (0 for X-axis, 1 for Y-axis).

    Returns:
        int or None: The period of the given axis if found, or None if no period is detected.
    """
    orthogonal_lines = find_orthogonal_lines(points)
    line = orthogonal_lines[axis - 1]
    labels = [point[2] for point in points if point[1] in line]
    differences = [labels[i - 1] - labels[i] for i in range(len(labels) - 1)]
    return abs(max(set(differences), key=differences.count) if differences else None)


def remove_overlapping_rectangles(rectangles):
    """
    Remove overlapping rectangles from the list of rectangles.

    Parameters:
        rectangles (list): List of rectangles in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].

    Returns:
        list: A list of non-overlapping rectangles.
    """
    unique_rectangles = []
    for rect in rectangles:
        is_overlapping = any(is_rect_overlapping(rect[0], unique_rect[0]) for unique_rect in unique_rectangles)

        if not is_overlapping:
            unique_rectangles.append(rect)
    return unique_rectangles


def is_rect_overlapping(rect1, rect2):
    """
    Check if two rectangles are overlapping.

    Parameters:
        rect1 (list): The first rectangle in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        rect2 (list): The second rectangle in the same format as rect1.

    Returns:
        bool: True if the rectangles are overlapping, False otherwise.
    """
    x1_min = min(coord[0] for coord in rect1)
    y1_min = min(coord[1] for coord in rect1)
    x1_max = max(coord[0] for coord in rect1)
    y1_max = max(coord[1] for coord in rect1)
    x2_min = min(coord[0] for coord in rect2)
    y2_min = min(coord[1] for coord in rect2)
    x2_max = max(coord[0] for coord in rect2)
    y2_max = max(coord[1] for coord in rect2)
    return x1_max >= x2_min and x1_min <= x2_max and y1_max >= y2_min and y1_min <= y2_max


def find_intersection(points, pixel_tolerance=1):
    """
    Find the intersection point of two orthogonal lines among the given points.

    Parameters:
        points (list): List of points in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        pixel_tolerance (int, optional): The maximum allowable difference in pixel coordinates for lines to be considered orthogonal. Default is 1.

    Returns:
        tuple: The (x, y) coordinates of the intersection point.

    Raises:
        ValueError: If no intersection point is found.
    """
    orthogonal_lines = []
    for i in range(len(points) - 1):
        for j in range(i + 1, len(points)):
            dx = points[i][1][0] - points[j][1][0]
            dy = points[i][1][1] - points[j][1][1]
            if abs(dx) <= pixel_tolerance < abs(dy):
                line = points[i][1], points[j][1]
                orthogonal_lines.append(line)
            elif abs(dx) > pixel_tolerance >= abs(dy):
                line = points[j][1], points[i][1]
                orthogonal_lines.append(line)
    for line1 in orthogonal_lines:
        for line2 in orthogonal_lines:
            if line1 != line2 and are_lines_orthogonal(line1, line2, angle_tolerance=5):
                x1, y1 = line1[0]
                x2, y2 = line1[1]
                x3, y3 = line2[0]
                x4, y4 = line2[1]
                xdiff = x1 - x2, x3 - x4
                ydiff = y1 - y2, y3 - y4
                div = xdiff[0] * ydiff[1] - xdiff[1] * ydiff[0]
                if div == 0:
                    continue
                d = x1 * y2 - y1 * x2, x3 * y4 - y3 * x4
                x = (d[0] * xdiff[1] - d[1] * xdiff[0]) / div
                y = (d[0] * ydiff[1] - d[1] * ydiff[0]) / div
                return x, y
    raise ValueError("Lines do not intersect")


def find_center_period(points, axis):
    """
    Find the center period of the given axis based on the points.

    Parameters:
        points (list): List of points in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        axis (int): The axis to find the center period for (0 for X-axis, 1 for Y-axis).

    Returns:
        int: The center period of the given axis.
    """
    sorted_points = sorted(points, key=lambda point: point[1][axis])
    gaps = [
        abs(sorted_points[i + 1][1][axis] - sorted_points[i][1][axis])
        for i in range(len(sorted_points) - 1)
    ]
    return int(sum(gaps) / len(gaps))


def are_lines_orthogonal(line1, line2, angle_tolerance=5):
    """
    Check if two lines are orthogonal.

    Parameters:
        line1 (list): The first line defined by two points [point1, point2].
        line2 (list): The second line defined by two points [point1, point2].
        angle_tolerance (float, optional): The maximum allowable difference in angle degrees for the lines to be considered orthogonal. Default is 5.

    Returns:
        bool: True if the lines are orthogonal, False otherwise.
    """
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1)) - math.degrees(math.atan2(y4 - y3, x4 - x3))

    return abs(angle - 90) <= angle_tolerance or abs(abs(angle) - 270) <= angle_tolerance


def find_orthogonal_lines(points, pixel_tolerance=1):
    """
    Find pairs of orthogonal lines among the given points.

    Parameters:
        points (list): List of points in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        pixel_tolerance (int, optional): The maximum allowable difference in pixel coordinates for lines to be considered orthogonal. Default is 1.

    Returns:
        list: A list of pairs of orthogonal lines, each defined by two points [point1, point2].
    """
    orthogonal_lines = []

    for i in range(len(points) - 1):
        for j in range(i + 1, len(points)):
            dx = points[i][1][0] - points[j][1][0]
            dy = points[i][1][1] - points[j][1][1]
            if abs(dx) <= pixel_tolerance:
                line = [points[i][1], points[j][1]]
                orthogonal_lines.append(line)
            elif abs(dy) <= pixel_tolerance:
                line = [points[j][1], points[i][1]]
                orthogonal_lines.append(line)
            if len(orthogonal_lines) == 2:
                line1 = orthogonal_lines[0]
                line2 = orthogonal_lines[1]
                if are_lines_orthogonal(line1, line2, angle_tolerance=5):
                    break
    return orthogonal_lines


def axis_coordinates_periods(line, axis):
    """
    Calculate the differences in coordinates along the specified axis for a line.

    Parameters:
        line (list): The line defined by two points [point1, point2].
        axis (int): The axis to calculate the differences for (0 for X-axis, 1 for Y-axis).

    Returns:
        list: A list of differences in coordinates along the specified axis.
    """
    return [line[i + 1][axis] - line[i][axis] for i in range(len(line) - 1)]


def find_missing_points(points, period_x, period_y, pixel_tolerance=1):
    """
    Find missing points on the axis based on the given points, center periods, and label periods.

    Parameters:
        points (list): List of points in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        period_x (int): The center period of the X-axis.
        period_y (int): The center period of the Y-axis.
        pixel_tolerance (int, optional): The maximum allowable difference in pixel coordinates. Default is 1.

    Returns:
        list: A list of missing points in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
    """
    missing_points = []
    lines = find_orthogonal_lines(points, pixel_tolerance)
    line1 = lines[0]
    line2 = lines[1]
    label_period_x = find_period(points, 0)
    label_period_y = find_period(points, 1)
    min_x = min(points, key=lambda point: point[1][0])[1][0]
    max_x = max(points, key=lambda point: point[1][0])[1][0]
    min_y = min(points, key=lambda point: point[1][1])[1][1]
    max_y = max(points, key=lambda point: point[1][1])[1][1]
    existing_labels_x = [float(point[2]) for point in points if point[1] in line2]
    existing_labels_y = [float(point[2]) for point in points if point[1] in line1]
    dx = []
    dy = []
    for point in points:
        dx.append(point[0][1][0] - point[0][0][0])
        dy.append(point[0][2][1] - point[0][1][1])
    w = sum(dx) / len(dx)
    h = sum(dy) / len(dy)
    for x in range(int(min_x), int(max_x), period_x):
        found = any(abs(point[1][1] - line2[0][1]) <= pixel_tolerance for point in points)
        if not found:
            label = max(existing_labels_x + [0]) - label_period_x
            while label in existing_labels_x:
                label -= label_period_x
            y = line2[0][1]
            rect = [[x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2], [x - w / 2, y + h / 2]]

            overlap = any(is_rect_overlapping(rect, point[0]) for point in points if point[1] in line2)
            if not overlap:
                missing_points.append([rect, [x, y], label])
                existing_labels_x.append(label)
    for y in range(int(min_y), int(max_y), period_y):
        found = any(abs(point[1][1] - y) <= pixel_tolerance for point in points)
        if not found:
            label = max(existing_labels_y + [0]) - label_period_y
            while label in existing_labels_y:
                label -= label_period_y
            x = line1[0][0]
            rect = [[x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2], [x - w / 2, y + h / 2]]
            overlap = any(is_rect_overlapping(rect, point[0]) for point in points if point[1] in line1)
            if not overlap:
                missing_points.append([rect, [x, y], label])
                existing_labels_y.append(label)
    return missing_points


def separate_lines(points, pixel_tolerance=1):
    """
    Separate points into X and Y parallel lines.

    Parameters:
        points (list): List of points in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        pixel_tolerance (int, optional): The maximum allowable difference in pixel coordinates. Default is 1.

    Returns:
        tuple: Two lists of points separated by X and Y parallel lines.
    """
    x_parallel_line = []
    y_parallel_line = []
    for i in range(len(points) - 1):
        if abs(int(points[i][1][1]) - int(points[i + 1][1][1])) <= pixel_tolerance:
            if points[i] not in x_parallel_line:
                x_parallel_line.append(points[i])
            if points[i + 1] not in x_parallel_line:
                x_parallel_line.append(points[i + 1])
        elif abs(int(points[i][1][0]) - int(points[i + 1][1][0])) <= pixel_tolerance:
            if points[i] not in y_parallel_line:
                y_parallel_line.append(points[i])
            if points[i + 1] not in y_parallel_line:
                y_parallel_line.append(points[i + 1])
    return x_parallel_line, y_parallel_line


def find_actual_points(points, pixel_tolerance=1):
    """
    Find the actual points (intersections) on the X and Y axes.

    Parameters:
        points (list): List of points in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
        pixel_tolerance (int, optional): The maximum allowable difference in pixel coordinates. Default is 1.

    Returns:
        tuple: Two lists of actual points (intersections) on the X and Y axes, each point in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
    """
    x_parallel_line, y_parallel_line = separate_lines(points, pixel_tolerance)
    lines_x = sorted(x_parallel_line, key=lambda point: point[2])
    lines_y = sorted(y_parallel_line, key=lambda point: point[2])
    x_zero_point = lines_x[0]
    y_zero_point = lines_y[0]
    x1, y1 = x_zero_point[1]
    x2, y2 = y_zero_point[1]
    if abs(y1 - y2) <= pixel_tolerance:
        raise ValueError("Lines are parallel")
    intersection_x = x_zero_point[1][0]
    intersection_y = y_zero_point[1][1]
    actual_points_x = [[[intersection_x, intersection_y], [x_zero_point[2], y_zero_point[2]]]]
    actual_points_y = [[[intersection_x, intersection_y], [x_zero_point[2], y_zero_point[2]]]]
    for point in lines_x[1:]:
        coords = point[1]
        label = [point[2], y_zero_point[2]]
        x_projection = coords[0]
        y_projection = intersection_y
        actual_points_x.append([[x_projection, y_projection], label])
    for point in lines_y[1:]:
        coords = point[1]
        label = [x_zero_point[2], point[2]]
        x_projection = intersection_x
        y_projection = coords[1]
        actual_points_y.append([[x_projection, y_projection], label])
    return actual_points_x, actual_points_y


def find_points(img_path):
    """
    Find the actual points (intersections) on the X and Y axes in a scientific figure image.

    Parameters:
        img_path (str): The path to the scientific figure image.

    Returns:
        list: A list of actual points (intersections) on the X and Y axes, each point in the format [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [center_x, center_y], label].
    """
    points = []
    for lang in [
        "latin",
        "arabic",
        "cyrillic",
        "devanagari",
        "ch",
    ]:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        result = ocr.ocr(str(img_path), cls=True)
        for r in result:
            points.extend([line[0], None, float(line[1][0])] for line in r if line[1][0].isnumeric())
    points = sorted(points, key=lambda rect: rect[0][0][0])
    points = remove_overlapping_rectangles(remove_duplicate_rectangles(points))
    for point in points:
        coords = point[0]
        x = [coord[0] for coord in coords]
        y = [coord[1] for coord in coords]
        center_x = int((min(x) + max(x)) / 2)
        center_y = int((min(y) + max(y)) / 2)
        points[points.index(point)][1] = [center_x, center_y]
    center_period_x = find_center_period(points, axis=0) * 2
    center_period_y = find_center_period(points, axis=1) * 2
    missing_points = find_missing_points(points, center_period_x, center_period_y, pixel_tolerance=1)
    points.extend(missing_points)
    points = sorted(points, key=lambda rect: rect[0][0][0])
    actual_points_x, actual_points_y = find_actual_points(points, pixel_tolerance=1)
    return [actual_points_x[0], actual_points_x[1], actual_points_y[1]]
