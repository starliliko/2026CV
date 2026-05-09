# ROS 2 Workspace

This workspace upgrades the repository toward a more complete
`PX4 + Gazebo + ROS 2 + Vision` learning project.

## What is included

1. `low_altitude_bringup` ROS 2 package skeleton
2. `ros_gz_bridge` config for `/clock`
3. `ros_gz_image` integration for the Gazebo camera topic
4. `image_snapshot` for saving periodic ROS 2 image frames to disk
5. `yolo_detector` as the ROS 2 detector entry point after runtime setup
6. HUD overlay + rich dashboard merged into `yolo_detector`
7. Modular helpers: `metrics.py`, `hud.py`, `dashboard.py`, `results_recorder.py`
8. JSONL detection log + rolling `summary.json` artifact for offline reporting

## Suggested workflow

1. Start PX4 and Gazebo
2. Bridge the Gazebo camera topic into ROS 2
3. Save sample frames with `image_snapshot` when you need a quick disk snapshot
4. Switch to `yolo_detector` after installing the YOLO runtime dependencies
5. Use the built-in HUD overlay and dashboard to validate throughput and latency
6. Add `px4_msgs` and `Micro XRCE-DDS Agent` when you begin closed-loop work

## Layout

```text
ros2_ws/
|-- src/
|   `-- low_altitude_bringup/
`-- README.md
```

## Build

```bash
source /opt/ros/humble/setup.bash
cd /mnt/d/2026CV/ros2_ws
colcon build
source install/setup.bash
```

## Launch options

Bridge only:

```bash
ros2 launch low_altitude_bringup sim_bridge.launch.py \
  gz_image_topic:=/world/baylands/model/x500_gimbal_0/link/camera_link/sensor/camera/image
```

Bridge plus debug perception nodes:

```bash
ros2 launch low_altitude_bringup perception_yolo.launch.py \
  gz_image_topic:=/world/baylands/model/x500_gimbal_0/link/camera_link/sensor/camera/image \
  enable_hud:=true \
  enable_dashboard:=true
```

Bridge plus YOLO detector:

```bash
ros2 launch low_altitude_bringup perception_yolo.launch.py \
  gz_image_topic:=/world/baylands/model/x500_gimbal_0/link/camera_link/sensor/camera/image \
  model_path:=yolov8n.pt \
  enable_hud:=true \
  enable_dashboard:=true
```

The detector writes snapshots into:

```text
/mnt/d/2026CV/demo/ros2_outputs
```

## Notes

1. The current launch defaults assume the `baylands` world and `x500_gimbal_0`
   model.
2. If you switch worlds or models, update `gz_image_topic` when launching.
3. `gz_bridge_clock.yaml` only handles `/clock`; image transport is handled by
  `ros_gz_image`.
4. The perception pipeline has been simplified to a 3-process launch: bridge,
  camera bridge, and `yolo_detector`.
