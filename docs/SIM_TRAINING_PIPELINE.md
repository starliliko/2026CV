# 仿真自动标注 → YOLO 微调 → ROS 2 部署 端到端流程

本文档串起 PR-1 ~ PR-4 的全部脚本，给出从空仿真到部署对比报告的可复现流程。所有命令都按 **Windows + WSL2 Ubuntu 22.04** 的混合工作流书写：仿真和数据采集在 WSL（ROS 2 Humble + Gazebo Harmonic），训练在 Windows 原生 Python（CUDA on RTX 4050 Laptop）。

---

## 0. 一次性准备

### Windows 训练环境
```powershell
# 在 D:\2026CV 下：
pwsh -File vision\setup_train_env.ps1
# 该脚本会创建 vision\.venv-train，安装 PyTorch CUDA 12.1 + ultralytics + 其余依赖，
# 并打印 torch.cuda.is_available() 的结果，确认 GPU 可见。
```

### WSL ROS 2 / Gazebo 环境
```bash
# 已存在 (ros-humble + gz harmonic + low_altitude_bringup)
cd /mnt/d/2026CV/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

---

## 1. 启动仿真世界并放置目标

```bash
# 终端 A — PX4 SITL
cd ~/PX4-Autopilot
PX4_GZ_WORLD=baylands make px4_sitl gz_x500_gimbal
# 在 Gazebo 窗口点 ▶ 让仿真运行
```

```bash
# 终端 B — Spawn 训练目标 (随机 8–15 个 car/truck/person/cone/boat)
cd /mnt/d/2026CV
python3 sim/launch/spawn_targets.py --world baylands --seed 42
# 写入 sim/runtime/spawned_<timestamp>.json + spawned_latest.json
```

清单文件后续给数据采集器读取。

---

## 2. 采集训练数据

```bash
# 终端 C — 启 ROS 2 桥 + 数据采集
ros2 launch low_altitude_bringup dataset_collect.launch.py \
    output_dir:=/mnt/d/2026CV/dataset/sim_v1 \
    target_total_frames:=5000 \
    capture_hz:=2.0
```

```bash
# 终端 D — 让无人机随机巡飞 ~40 分钟
cd /mnt/d/2026CV
python3 sim/missions/random_waypoints.py --duration 2400 --seed 7
```

**产出**：`dataset/sim_v1/images/raw/*.jpg` + `dataset/sim_v1/labels/raw/*.txt`（YOLO 格式）。

> 验证质量：用任意标注预览工具打开几张 raw 图，确认绿色框对齐车辆/行人。如果系统性偏移，多半是 `camera_link_name` 或 `camera_pose_gz_topic` 参数未匹配你的 PX4 模型，按你实际话题修改 launch 参数。

---

## 3. 切分 & 构建 YOLO 数据集

在 Windows PowerShell（任何 Python 环境，数据集只是文件操作）：

```powershell
cd D:\2026CV
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

## 4. 训练 YOLOv8s（Windows 原生 + RTX 4050）

```powershell
# 进入训练专用 venv
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

**预期**：5000 张 / 50 epoch ≈ 1 小时。产出：
- `runs/sim/v1/weights/best.pt` — 最优权重
- `runs/sim/v1/results.png` — loss/mAP 曲线
- `runs/sim/v1/confusion_matrix.png`
- `runs/sim/v1/val_batch*_pred.jpg` — 推理可视化

把 best.pt 复制为部署副本：
```powershell
Copy-Item runs\sim\v1\weights\best.pt ros2_ws\yolov8s-sim-v1.pt
```

---

## 5. 部署回 ROS 2 推理管线 + 对比报告

```bash
# WSL 终端
ros2 launch low_altitude_bringup perception_yolo.launch.py \
    model_path:=/mnt/d/2026CV/ros2_ws/yolov8s-sim-v1.pt \
    confidence:=0.20 \
    results_dir:=/mnt/d/2026CV/demo/ros2_outputs/sim_v1
```

让无人机再飞 1–2 分钟同一航迹，然后停止、转 Markdown 报告：

```powershell
# Windows
python vision\summarize_results.py `
    --jsonl D:\2026CV\demo\ros2_outputs\sim_v1\detections.jsonl `
    --output D:\2026CV\demo\ros2_outputs\report_sim_v1.md
```

**对比基线**：用同样脚本对 COCO yolov8n 跑一份 `report_coco.md`，两份并排即是答辩 PPT 的「自训 vs 预训练」一页。

---

## 6. 故障排查

| 现象 | 排查 |
|---|---|
| spawn 失败 / 模型不出现 | 确认 Gazebo 已启动且世界名为 `baylands`；首次下载 Fuel 模型需要外网 |
| 标签框系统性偏移 | 检查 `camera_link_name`、`camera_pose_gz_topic` 是否匹配实际 PX4 模型；查 `gz topic -l` |
| `frame_count: 0` | Gazebo 暂停；点 ▶ |
| `torch.cuda.is_available() = False` | 重新跑 setup_train_env，确认 NVIDIA 驱动 ≥ 535；用 `nvidia-smi` 确认显卡 |
| 训练 OOM | 把 `--batch` 降到 8 或 `--imgsz` 降到 512 |
| MAVSDK 连接超时 | PX4 默认 14540，确认终端已运行 `make px4_sitl gz_x500_gimbal` 且仿真在跑 |

---

## 7. 文件索引

| 路径 | 作用 |
|---|---|
| [sim/configs/target_models.yaml](../sim/configs/target_models.yaml) | 目标类别 + Fuel 模型 + AABB 大小 |
| [sim/launch/spawn_targets.py](../sim/launch/spawn_targets.py) | 在仿真中随机 spawn 目标 |
| [sim/missions/random_waypoints.py](../sim/missions/random_waypoints.py) | 无人机随机巡飞 (MAVSDK) |
| [vision/dataset/projection.py](../vision/dataset/projection.py) | 3D AABB → 2D bbox 投影核心 |
| [vision/dataset/build_yolo_dataset.py](../vision/dataset/build_yolo_dataset.py) | train/val 切分 + dataset.yaml 生成 |
| [vision/train_sim.py](../vision/train_sim.py) | YOLOv8 训练入口（Ultralytics 包装） |
| [vision/setup_train_env.ps1](../vision/setup_train_env.ps1) | Windows 训练 venv 安装器 |
| [vision/requirements-train.txt](../vision/requirements-train.txt) | 训练 venv 依赖清单 |
| [ros2_ws/src/low_altitude_bringup/low_altitude_bringup/dataset_collector.py](../ros2_ws/src/low_altitude_bringup/low_altitude_bringup/dataset_collector.py) | ROS 2 数据采集 + 自动标注节点 |
| [ros2_ws/src/low_altitude_bringup/launch/dataset_collect.launch.py](../ros2_ws/src/low_altitude_bringup/launch/dataset_collect.launch.py) | 一键启动桥 + 采集 |
| [vision/summarize_results.py](../vision/summarize_results.py) | JSONL → Markdown 报告 |
