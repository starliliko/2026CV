# ROS 2 工作区

`ros2_ws` 包含 `low_altitude_bringup` ROS 2 Python 包，负责 Gazebo 桥接、图像限流、YOLO 推理、HUD、运行统计和仿真数据采集。

## 构建

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
colcon build --packages-select low_altitude_bringup --symlink-install
source install/setup.bash
```

## 主要启动文件

- `sim_bridge.launch.py`：桥接仿真时钟和相机图像
- `perception_yolo.launch.py`：桥接、图像限流和 YOLO 检测
- `dataset_collect.launch.py`：仿真图像与 3D 目标投影采集

仅启动感知链路：

```bash
bash scripts/run_demo.sh
```

检测节点发布：

- `/camera/annotated`
- `/detections/yolo`
- `demo/ros2_outputs/detections.jsonl`
- `demo/ros2_outputs/summary.json`

运行参数、话题和环境说明见 [docs/architecture.md](../docs/architecture.md) 与 [docs/reproduction.md](../docs/reproduction.md)。
