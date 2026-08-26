import pytest

from src.point_cloud import (
    PointCloud, count_points_in_box, count_points_in_radius, bounding_box,
)

SAMPLE_PCD = """
# sample point cloud, 6 points
0.0 0.0 0.0
1.0 1.0 1.0
2.0 2.0 2.0
-1.0 0.5 0.2
5.0 5.0 5.0
0.1 0.1 0.1
"""


def test_parses_correct_point_count():
    cloud = PointCloud.from_ascii_pcd(SAMPLE_PCD)
    assert len(cloud) == 6


def test_ignores_comments_and_blank_lines():
    text = "# header\n\n1.0 2.0 3.0\n\n# another comment\n4.0 5.0 6.0\n"
    cloud = PointCloud.from_ascii_pcd(text)
    assert len(cloud) == 2


def test_malformed_line_raises():
    with pytest.raises(ValueError):
        PointCloud.from_ascii_pcd("1.0 2.0\n")  # only 2 values


def test_empty_input_gives_empty_cloud():
    cloud = PointCloud.from_ascii_pcd("")
    assert len(cloud) == 0


def test_count_points_in_box_correct():
    cloud = PointCloud.from_ascii_pcd(SAMPLE_PCD)
    # box covering roughly the origin cluster: (0,0,0), (1,1,1), (-1,0.5,0.2), (0.1,0.1,0.1)
    count = count_points_in_box(cloud, x_range=(-1.5, 1.5), y_range=(-1.5, 1.5), z_range=(-1.5, 1.5))
    assert count == 4


def test_count_points_in_box_excludes_outliers():
    cloud = PointCloud.from_ascii_pcd(SAMPLE_PCD)
    count = count_points_in_box(cloud, x_range=(4.0, 6.0), y_range=(4.0, 6.0), z_range=(4.0, 6.0))
    assert count == 1  # only the (5,5,5) point


def test_count_points_in_box_empty_cloud():
    cloud = PointCloud.from_ascii_pcd("")
    assert count_points_in_box(cloud, (0, 1), (0, 1), (0, 1)) == 0


def test_count_points_in_radius_correct():
    cloud = PointCloud.from_ascii_pcd(SAMPLE_PCD)
    # radius around origin should catch the tight cluster near (0,0,0)
    count = count_points_in_radius(cloud, center=(0.0, 0.0, 0.0), radius=0.2)
    assert count == 2  # (0,0,0) and (0.1,0.1,0.1)


def test_count_points_in_radius_large_radius_catches_all():
    cloud = PointCloud.from_ascii_pcd(SAMPLE_PCD)
    count = count_points_in_radius(cloud, center=(0.0, 0.0, 0.0), radius=100.0)
    assert count == 6


def test_bounding_box_correct():
    cloud = PointCloud.from_ascii_pcd(SAMPLE_PCD)
    mins, maxs = bounding_box(cloud)
    assert mins == (-1.0, 0.0, 0.0)
    assert maxs == (5.0, 5.0, 5.0)


def test_bounding_box_empty_raises():
    cloud = PointCloud.from_ascii_pcd("")
    with pytest.raises(ValueError):
        bounding_box(cloud)
