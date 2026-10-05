"""
Basic 3D point-cloud utilities: parsing a simplified ASCII PCD-style
format, counting points within a defined region of interest, and
detecting clusters -- the shape of manually counting points within
the 3D point cloud space, done
programmatically and verifiably rather than by eye.

Does not depend on open3d (not installed in this environment) --
implemented directly with plain Python/NumPy so the logic is fully
inspectable and testable without an external point-cloud library
dependency. See README for the honest disclosure on this substitution.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PointCloud:
    points: np.ndarray  # shape (N, 3) -- x, y, z in meters

    @classmethod
    def from_ascii_pcd(cls, text: str) -> "PointCloud":
        """Parses a simplified ASCII point-cloud format: one 'x y z'
        triple per line, blank lines and lines starting with '#'
        ignored (mirroring a minimal PCD-like text layout)."""
        rows = []
        for line in text.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"malformed point-cloud line (expected 3 values): {line!r}")
            rows.append([float(p) for p in parts])
        if not rows:
            return cls(points=np.empty((0, 3)))
        return cls(points=np.array(rows, dtype=float))

    def __len__(self) -> int:
        return len(self.points)


def count_points_in_box(cloud: PointCloud, x_range: tuple[float, float],
                         y_range: tuple[float, float], z_range: tuple[float, float]) -> int:
    """Counts points within an axis-aligned bounding box -- the
    programmatic equivalent of manually counting points within a region
    of the point cloud, e.g. to validate object-detection output against
    a known reference count."""
    if len(cloud) == 0:
        return 0
    pts = cloud.points
    mask = (
        (pts[:, 0] >= x_range[0]) & (pts[:, 0] <= x_range[1]) &
        (pts[:, 1] >= y_range[0]) & (pts[:, 1] <= y_range[1]) &
        (pts[:, 2] >= z_range[0]) & (pts[:, 2] <= z_range[1])
    )
    return int(mask.sum())


def count_points_in_radius(cloud: PointCloud, center: tuple[float, float, float], radius: float) -> int:
    """Counts points within a given radius of a center point -- a
    second, distinct region-of-interest shape (sphere rather than box)
    for validating a detected object's point density."""
    if len(cloud) == 0:
        return 0
    center_arr = np.array(center)
    distances = np.linalg.norm(cloud.points - center_arr, axis=1)
    return int((distances <= radius).sum())


def bounding_box(cloud: PointCloud) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Returns (min_xyz, max_xyz) for the cloud -- used to sanity-check
    that a parsed cloud's extent matches an expected sensor range."""
    if len(cloud) == 0:
        raise ValueError("cannot compute bounding box of an empty point cloud")
    mins = cloud.points.min(axis=0)
    maxs = cloud.points.max(axis=0)
    return tuple(mins.tolist()), tuple(maxs.tolist())
