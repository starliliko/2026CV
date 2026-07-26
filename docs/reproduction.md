# 环境与复现

## 已验证环境

- Ubuntu 24.04（保存在移动硬盘中，通过 VirtualBox 制作和运行）
- ROS 2 Jazzy
- Gazebo Harmonic
- PX4 v1.16
- Python 3.12
- Windows 11 + RTX 4050（用于模型训练）

虚拟机无法直接使用宿主机 NVIDIA GPU，因此 Ubuntu 默认安装 CPU 版 PyTorch。项目路径可以自由选择，脚本会根据自身位置定位仓库，不依赖固定的绝对路径。

## 外部依赖

PX4 源码需要单独安装，默认路径为：

```bash
~/PX4/PX4-Autopilot
```

如路径不同，启动时设置：

```bash
PX4_DIR=/path/to/PX4-Autopilot bash scripts/launch_all.sh
```

## Ubuntu 推理环境

```bash
git clone https://github.com/starliliko/2026CV.git
cd 2026CV

bash vision/setup_infer_env.sh
source vision/.venv-train/bin/activate
bash scripts/download_model.sh
```

构建 ROS 2 工作区：

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
colcon build --packages-select low_altitude_bringup --symlink-install
cd ..
```

## 启动完整演示

```bash
bash scripts/launch_all.sh
```

常用参数：

```bash
WORLD=baylands_2026cv bash scripts/launch_all.sh
DEVICE=cpu IMGSZ=320 bash scripts/launch_all.sh
WITH_MISSION=1 bash scripts/launch_all.sh
PX4_DIR=/path/to/PX4-Autopilot bash scripts/launch_all.sh
```

查看标注图像：

```bash
bash scripts/view_annotated.sh
```

停止进程：

```bash
bash scripts/stop_all.sh
```

## 只启动 ROS 2 感知

PX4 和 Gazebo 已经运行时：

```bash
bash scripts/run_demo.sh
```

输出保存在 `demo/ros2_outputs/`。该目录中的运行数据默认由 Git 忽略。

## 离线图片推理

```bash
source vision/.venv-train/bin/activate
python vision/run_detection.py path/to/image.jpg \
  --model ros2_ws/yolov8n.pt \
  --output demo/offline_outputs
```

输入也可以是图片目录或视频文件。

## Windows 训练

```powershell
pwsh -File vision\setup_train_env.ps1
.\vision\.venv-train\Scripts\Activate.ps1
python vision\train_sim.py --data path\to\dataset.yaml
```

训练产生的 `.pt` 权重不提交到 Git。需要部署时，将权重复制到 `ros2_ws/`，并通过 `model_path` 指定：

```bash
ros2 launch low_altitude_bringup perception_yolo.launch.py \
  model_path:="$PWD/ros2_ws/custom-best.pt"
```

## 结果汇总

```bash
python vision/summarize_results.py \
  --jsonl demo/ros2_outputs/detections.jsonl \
  --output demo/ros2_outputs/report.md
```
