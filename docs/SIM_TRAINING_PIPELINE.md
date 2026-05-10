# 仿真自动标注 → YOLO 微调 → ROS 2 部署 端到端流程

本文档串起 PR-1 ~ PR-4 的全部脚本，给出从空仿真到部署对比报告的可复现流程。环境划分如下：

| 阶段                                | 运行在                                                  | 原因                                                                                                                                                                                                          |
| ----------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 仿真 / 数据采集 / ROS 2 推理 / 报告 | **原生 Ubuntu 24.04**（本项目位于 `/home/libo/2026CV`） | ROS 2 Jazzy + Gazebo Harmonic + PX4 SITL 都在 Linux 运行                                                                                                                                                      |
| **YOLOv8 训练 / 微调**              | **Windows 安装（宿主）**                                | 当前 Linux 跑在 VirtualBox VM 里，VBox 不支持 NVIDIA GPU PCIe passthrough，`nvidia-smi` 不可用，`torch.cuda.is_available()` 总是 False。CPU 训练 yolov8s 太慢，于是训练这一步回到 Windows 本机调用 RTX 4050。 |

交接点：训练产出的 `best.pt` 拷贝回 Linux 侧 `ros2_ws/`，交给 `yolo_detector` 节点推理。

---

## 0. 一次性准备

### Linux 侧：推理 venv
```bash
cd /home/libo/2026CV
bash vision/setup_infer_env.sh                 # 默认 CPU、仅推理够用
# 裸机 Linux + NVIDIA 驱动可选：CUDA=cu121 bash vision/setup_infer_env.sh
source vision/.venv-train/bin/activate
```
该脚本会在 `vision/.venv-train/` 创建独立 venv，装 PyTorch + Ultralytics + numpy<2 等，供 ROS 2 节点与 `summarize_results.py` 使用。

### Linux 侧：ROS 2 / Gazebo
```bash
source /opt/ros/jazzy/setup.bash
cd /home/libo/2026CV/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### Windows 侧：训练 venv（宿主机，RTX 4050 + CUDA 12.1）
```powershell
# 在 D:\2026CV 下（Windows 能访问移动硬盘上的同一仓库）
pwsh -File vision\setup_train_env.ps1
# 该脚本会创建 vision\.venv-train，装 PyTorch CUDA 12.1 + ultralytics + 其余依赖，
# 并打印 torch.cuda.is_available()，确认 GPU 可见。
```
> 注意：Windows 与 Linux 各自维护 `vision/.venv-train`；两者不能同时存在于同一路径。如果 Windows 也挂载了这块移动硬盘上的 Linux ext4 分区（一般访问不了），请在 Windows 侧独立存放项目代码。

---

## 1. 启动仿真世界并放置目标

```bash
# 终端 A — PX4 SITL
cd ~/PX4/PX4-Autopilot
PX4_GZ_WORLD=baylands make px4_sitl gz_x500_gimbal
# 在 Gazebo 窗口点 ▶ 让仿真运行
```

```bash
# 终端 B — Spawn 训练目标 (随机 8–15 个 car/truck/person/cone/boat)
cd /home/libo/2026CV
python3 sim/launch/spawn_targets.py --world baylands --seed 42
# 写入 sim/runtime/spawned_<timestamp>.json + spawned_latest.json
```

清单文件后续给数据采集器读取。

---

## 2. 采集训练数据

```bash
# 终端 C — 启 ROS 2 桥 + 数据采集
ros2 launch low_altitude_bringup dataset_collect.launch.py \
    output_dir:=/home/libo/2026CV/dataset/sim_v1 \
    target_total_frames:=5000 \
    capture_hz:=2.0
```

```bash
# 终端 D — 让无人机随机巡飞 ~40 分钟
cd /home/libo/2026CV
python3 sim/missions/random_waypoints.py --duration 2400 --seed 7
```

**产出**：`dataset/sim_v1/images/raw/*.jpg` + `dataset/sim_v1/labels/raw/*.txt`（YOLO 格式）。

> 验证质量：用任意标注预览工具打开几张 raw 图，确认绿色框对齐车辆/行人。如果系统性偏移，多半是 `camera_link_name` 或 `camera_pose_gz_topic` 参数未匹配你的 PX4 模型，按你实际话题修改 launch 参数。

---

## 3. 切分 & 构建 YOLO 数据集（Windows）

数据集准备与训练位于同一侧（Windows）以避免跨系统拷贝。先把 Linux 采集出的 `dataset/sim_v1/` 拷到 Windows 侧同路径（或使用共享文件夹），然后：

```powershell
# Windows PowerShell
cd D:\2026CV
.\vision\.venv-train\Scripts\Activate.ps1
python vision\dataset\build_yolo_dataset.py `
    --root D:\2026CV\dataset\sim_v1 `
    --val-fraction 0.2 `
    --seed 0 `
    --copy
```

会生成：
- `dataset/sim_v1/images/{train,val}/`
- `dataset/sim_v1/labels/{train,val}/`
- `dataset/sim_v1/dataset.yaml`（含类别名映射）

---

## 4. 训练 YOLOv8s（Windows + RTX 4050 / CUDA 12.1）

```powershell
# Windows PowerShell
.\vision\.venv-train\Scripts\Activate.ps1

python vision\train_sim.py `
    --data D:\2026CV\dataset\sim_v1\dataset.yaml `
    --model yolov8s.pt `
    --imgsz 640 `
    --epochs 50 `
    --batch 16 `
    --device 0 `
    --name v1
```

**预期**：5000 张 / 50 epoch，RTX 4050 ≈ 1 小时。产出：
- `runs/sim/v1/weights/best.pt` — 最优权重
- `runs/sim/v1/results.png` — loss/mAP 曲线
- `runs/sim/v1/confusion_matrix.png`
- `runs/sim/v1/val_batch*_pred.jpg` — 推理可视化

复制训练产出到 Linux 侧部署位置。最简单的做法是把 `best.pt` 放在两侧都能访问的共享文件夹，或者用 `scp`：
```bash
# Linux 侧，从 Windows 位置拉过去（示意）
cp /mnt/share/best.pt /home/libo/2026CV/ros2_ws/yolov8s-sim-v1.pt
```

---

## 5. 部署回 ROS 2 推理管线 + 对比报告

```bash
# Linux ROS 2 终端（已 source jazzy + 工作区）
ros2 launch low_altitude_bringup perception_yolo.launch.py \
    model_path:=/home/libo/2026CV/ros2_ws/yolov8s-sim-v1.pt \
    confidence:=0.20 \
    results_dir:=/home/libo/2026CV/demo/ros2_outputs/sim_v1
```

让无人机再飞 1–2 分钟同一航迹，然后停止、转 Markdown 报告（Linux 推理 venv 里运行）：

```bash
source /home/libo/2026CV/vision/.venv-train/bin/activate
python /home/libo/2026CV/vision/summarize_results.py \
    --jsonl /home/libo/2026CV/demo/ros2_outputs/sim_v1/detections.jsonl \
    --output /home/libo/2026CV/demo/ros2_outputs/report_sim_v1.md
```

**对比基线**：用同样脚本对 COCO yolov8n 跑一份 `report_coco.md`，两份并排即是答辩 PPT 的「自训 vs 预训练」一页。

---

## 6. 故障排查

| 现象                                | 排查                                                                                    |
| ----------------------------------- | --------------------------------------------------------------------------------------- |
| spawn 失败 / 模型不出现             | 确认 Gazebo 已启动且世界名为 `baylands`；首次下载 Fuel 模型需要外网                     |
| 标签框系统性偏移                    | 检查 `camera_link_name`、`camera_pose_gz_topic` 是否匹配实际 PX4 模型；查 `gz topic -l` |
| `frame_count: 0`                    | Gazebo 暂停；点 ▶                                                                       |
| `torch.cuda.is_available() = False` | 重新跑 setup_train_env，确认 NVIDIA 驱动 ≥ 535；用 `nvidia-smi` 确认显卡                |
| 训练 OOM                            | 把 `--batch` 降到 8 或 `--imgsz` 降到 512                                               |
| MAVSDK 连接超时                     | PX4 默认 14540，确认终端已运行 `make px4_sitl gz_x500_gimbal` 且仿真在跑                |

---

## 7. 文件索引

| 路径                                                                                                                                                        | 作用                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| [sim/configs/target_models.yaml](../sim/configs/target_models.yaml)                                                                                         | 目标类别 + Fuel 模型 + AABB 大小                    |
| [sim/launch/spawn_targets.py](../sim/launch/spawn_targets.py)                                                                                               | 在仿真中随机 spawn 目标                             |
| [sim/missions/random_waypoints.py](../sim/missions/random_waypoints.py)                                                                                     | 无人机随机巡飞 (MAVSDK)                             |
| [vision/dataset/projection.py](../vision/dataset/projection.py)                                                                                             | 3D AABB → 2D bbox 投影核心                          |
| [vision/dataset/build_yolo_dataset.py](../vision/dataset/build_yolo_dataset.py)                                                                             | train/val 切分 + dataset.yaml 生成                  |
| [vision/train_sim.py](../vision/train_sim.py)                                                                                                               | YOLOv8 训练入口（Ultralytics 包装，Windows 侧运行） |
| [vision/setup_train_env.ps1](../vision/setup_train_env.ps1)                                                                                                 | Windows 训练 venv 安装器（PyTorch CUDA 12.1）       |
| [vision/setup_infer_env.sh](../vision/setup_infer_env.sh)                                                                                                   | Ubuntu 推理 venv 安装器（CPU / CUDA 可切换）        |
| [vision/requirements-train.txt](../vision/requirements-train.txt)                                                                                           | 训练 venv 依赖清单                                  |
| [ros2_ws/src/low_altitude_bringup/low_altitude_bringup/dataset_collector.py](../ros2_ws/src/low_altitude_bringup/low_altitude_bringup/dataset_collector.py) | ROS 2 数据采集 + 自动标注节点                       |
| [ros2_ws/src/low_altitude_bringup/launch/dataset_collect.launch.py](../ros2_ws/src/low_altitude_bringup/launch/dataset_collect.launch.py)                   | 一键启动桥 + 采集                                   |
| [vision/summarize_results.py](../vision/summarize_results.py)                                                                                               | JSONL → Markdown 报告                               |
