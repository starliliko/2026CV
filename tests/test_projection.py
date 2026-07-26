import pytest

from low_altitude_bringup.projection import (
    CameraIntrinsics,
    Pose,
    VisibilityFilter,
    project_aabb,
    to_yolo_line,
)


INTRINSICS = CameraIntrinsics(
    fx=500.0,
    fy=500.0,
    cx=320.0,
    cy=240.0,
    width=640,
    height=480,
)
CAMERA_POSE = Pose(
    xyz=(0.0, 0.0, 0.0),
    quat_xyzw=(0.0, 0.0, 0.0, 1.0),
)


def test_project_visible_box_and_convert_to_yolo() -> None:
    bbox = project_aabb(
        center_xyz=(10.0, 0.0, 0.0),
        yaw=0.0,
        size=(2.0, 2.0, 2.0),
        cam_pose=CAMERA_POSE,
        intrinsics=INTRINSICS,
    )

    assert bbox is not None
    x_min, y_min, x_max, y_max = bbox
    assert x_min < 320.0 < x_max
    assert y_min < 240.0 < y_max

    values = to_yolo_line(2, bbox, 640, 480).split()
    assert values[0] == "2"
    assert float(values[1]) == pytest.approx(0.5, abs=1e-6)
    assert float(values[2]) == pytest.approx(0.5, abs=1e-6)


def test_reject_box_behind_camera_or_too_far() -> None:
    assert (
        project_aabb(
            center_xyz=(-10.0, 0.0, 0.0),
            yaw=0.0,
            size=(2.0, 2.0, 2.0),
            cam_pose=CAMERA_POSE,
            intrinsics=INTRINSICS,
        )
        is None
    )
    assert (
        project_aabb(
            center_xyz=(200.0, 0.0, 0.0),
            yaw=0.0,
            size=(2.0, 2.0, 2.0),
            cam_pose=CAMERA_POSE,
            intrinsics=INTRINSICS,
            vis=VisibilityFilter(max_distance_m=150.0),
        )
        is None
    )
