# ref. https://bitbucket.org/william_rusnack/minimumboundingbox/src/master/MinimumBoundingBox.py

from math import sqrt
from math import atan2, cos, sin, pi
from collections import namedtuple

from scipy.spatial import ConvexHull
from numpy import dot, mean, arctan2, argsort, array


BoundingBox = namedtuple('BoundingBox', ('area',
                                         'length_parallel',
                                         'length_orthogonal',
                                         'rectangle_center',
                                         'unit_vector',
                                         'unit_vector_angle',
                                         'corner_points'
                                         ))


def unit_2d_vector(pt0, pt1):
    dis_0_to_1 = sqrt((pt0[0] - pt1[0]) ** 2 + (pt0[1] - pt1[1]) ** 2)
    return (pt1[0] - pt0[0]) / dis_0_to_1, (pt1[1] - pt0[1]) / dis_0_to_1


def orthogonal_2d_vector(vector):
    return -1 * vector[1], vector[0]


def bounding_area(index, hull):
    unit_vector_p = unit_2d_vector(hull[index], hull[index + 1])
    unit_vector_o = orthogonal_2d_vector(unit_vector_p)
    dis_p, dis_o = tuple(dot(unit_vector_p, pt) for pt in hull), tuple(dot(unit_vector_o, pt) for pt in hull)
    min_p, min_o = min(dis_p), min(dis_o)
    len_p, len_o = max(dis_p) - min_p, max(dis_o) - min_o
    return {
        'area': len_p * len_o,
        'length_parallel': len_p,
        'length_orthogonal': len_o,
        'rectangle_center': (min_p + len_p / 2, min_o + len_o / 2),
        'unit_vector': unit_vector_p
    }


def to_xy_coordinates(unit_vector_angle, pt):
    angle_orthogonal = unit_vector_angle + pi / 2
    return (
        pt[0] * cos(unit_vector_angle) + pt[1] * cos(angle_orthogonal),
        pt[0] * sin(unit_vector_angle) + pt[1] * sin(angle_orthogonal)
    )


def rotate_points(center_of_rotation, angle, pts):
    rot_points = []
    # ang = []
    for pt in pts:
        diff = tuple([pt[d] - center_of_rotation[d] for d in range(2)])
        diff_angle = atan2(diff[1], diff[0]) + angle
        diff_length = sqrt(sum([d ** 2 for d in diff]))
        # ang.append(diff_angle)
        rot_points.append((center_of_rotation[0] + diff_length * cos(diff_angle),
                           center_of_rotation[1] + diff_length * sin(diff_angle)))
    return rot_points


def sort_points_clockwise(pts):
    center = mean(pts, axis=0)
    angles = arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
    sorted_points = pts[argsort(angles)]
    return sorted_points


def rectangle_corners(rectangle):
    corner_points = [(rectangle['rectangle_center'][0] + i1 * rectangle['length_parallel'],
                      rectangle['rectangle_center'][1] + i2 * rectangle['length_orthogonal'])
                     for i1 in (.5, -.5) for i2 in (i1, -1 * i1)]
    return rotate_points(rectangle['rectangle_center'], rectangle['unit_vector_angle'], corner_points)


def minimum_bbox(pts):
    assert len(pts) > 2, 'More than 2 points required'

    hull_ordered = [pts[idx] for idx in ConvexHull(pts).vertices]
    hull_ordered.append(hull_ordered[0])

    min_rectangle = bounding_area(0, hull_ordered)
    for i in range(1, len(hull_ordered) - 1):
        rectangle = bounding_area(i, hull_ordered)
        if rectangle['area'] < min_rectangle['area']:
            min_rectangle = rectangle

    min_rectangle['unit_vector_angle'] = atan2(min_rectangle['unit_vector'][1], min_rectangle['unit_vector'][0])
    min_rectangle['rectangle_center'] = to_xy_coordinates(min_rectangle['unit_vector_angle'],
                                                          min_rectangle['rectangle_center'])

    return BoundingBox(
        area=min_rectangle['area'],
        length_parallel=min_rectangle['length_parallel'],
        length_orthogonal=min_rectangle['length_orthogonal'],
        rectangle_center=min_rectangle['rectangle_center'],
        unit_vector=min_rectangle['unit_vector'],
        unit_vector_angle=min_rectangle['unit_vector_angle'],
        corner_points=sort_points_clockwise(array(tuple(set(rectangle_corners(min_rectangle)))))
    )


# [Usage Example]
# points = [(1, 2), (5, 4), (-1, -3)]
# bounding_box = minimum_bbox(points)
# print(bounding_box.area)
# print(bounding_box.rectangle_center)
# print(bounding_box.corner_points)
# print(bounding_box.unit_vector)
# print(bounding_box.unit_vector_angle)
