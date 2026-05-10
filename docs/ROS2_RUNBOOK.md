# ROS 2 Runbook

This runbook documents the current `PX4 + Gazebo + ROS 2` workflow in this
repository.

## Current status

The following pieces are in place:

1. `ROS 2 Jazzy` is installed in `Ubuntu 24.04`
2. `ros_gz_bridge` is installed for `/clock`
3. `ros_gz_image` is installed for the Gazebo camera stream
4. `ros2_ws` builds with `colcon build`
5. `perception_yolo.launch.py` starts the bridge and the real detector node
6. HUD overlay and terminal dashboard are merged into `yolo_detector`

## Current node graph

The ROS 2 side currently includes:

1. `parameter_bridge`
2. `gazebo_camera_bridge`
3. `image_snapshot`
4. `yolo_detector`

Bridge configuration for non-image topics comes from:

`ros2_ws/src/low_altitude_bringup/config/gz_bridge_clock.yaml`

The Gazebo image stream is bridged separately with `ros_gz_image`.

## Recommended startup order

### 1. Start PX4 and Gazebo in WSL

```bash
cd ~/PX4/PX4-Autopilot
PX4_GZ_WORLD=baylands make px4_sitl gz_x500_gimbal
```

The current local setup expects the `baylands` world with the camera topic
below:

```text
/world/baylands/model/x500_gimbal_0/link/camera_link/sensor/camera/image
```

### 2. Confirm that Gazebo is actually publishing the camera topic

```bash
gz topic -l | grep camera
```

If no camera topic appears here, ROS 2 will not receive any image.

### 3. Build and source the ROS 2 workspace

```bash
source /opt/ros/jazzy/setup.bash
cd /home/libo/2026CV/ros2_ws
colcon build
source install/setup.bash
```

### 4. Start the ROS 2 bridge and perception nodes

```bash
ros2 launch low_altitude_bringup perception_yolo.launch.py \
  gz_image_topic:=/world/baylands/model/x500_gimbal_0/link/camera_link/sensor/camera/image \
  enable_hud:=true \
  enable_dashboard:=true
```

### 5. Start the YOLO detector launch after dependencies are installed

```bash
ros2 launch low_altitude_bringup perception_yolo.launch.py \
  gz_image_topic:=/world/baylands/model/x500_gimbal_0/link/camera_link/sensor/camera/image \
  model_path:=yolov8n.pt \
  enable_hud:=true \
  enable_dashboard:=true
```

## Expected behavior

When the bridge is healthy, you should see:

1. `parameter_bridge` creating `/clock`
2. `gazebo_camera_bridge` exposing `/camera/image_raw`
3. `image_snapshot` writing `.ppm` files into `demo/ros2_outputs/` when used
4. `yolo_detector` publishing JSON detection summaries
5. `yolo_detector` drawing the HUD and printing the dashboard stats
6. `detections.jsonl` and `summary.json` updating under `demo/ros2_outputs/`

## Common issues

### No image frames in `frame_monitor`

Typical causes:

1. Gazebo or PX4 is not actually running
2. The simulation is paused
3. The `gz_image_topic` launch argument does not match the real camera topic

Check:

```bash
gz topic -l | grep image
```

Then compare the real topic against the `gz_image_topic` value passed into the
launch file.

### `/clock` exists but `/camera/image_raw` stays empty

This usually means one of two things:

1. Gazebo is not publishing the camera topic yet
2. The camera topic path is correct for a different world or model

The current ROS launch defaults assume:

```text
world=baylands
model=x500_gimbal_0
```

### ROS 2 nodes start but no snapshot files appear

Check:

```bash
ls /home/libo/2026CV/demo/ros2_outputs
```

If the directory only contains `.gitkeep`, ROS 2 likely is not receiving images
yet.

### `yolo_detector` says the model is unavailable

The detector depends on:

1. `ultralytics`
2. `torch`
3. A compatible NumPy / OpenCV stack

The node is intentionally written to stay alive and publish a status message
instead of crashing when those packages are missing or mismatched.

## Current project stage

The project has moved from:

`Gazebo -> shared files -> Windows display`

to:

`Gazebo -> ros_gz_image + ros_gz_bridge -> ROS 2 topics -> one merged perception node`

## Recommended next steps

1. Keep the Gazebo camera bridge stable
2. Validate `perception_yolo.launch.py` while PX4 and Gazebo are actively running
3. Add a ROS 2 detection result recorder if you need offline metrics
4. Add `px4_msgs` after the image chain is stable
