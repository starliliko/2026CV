# 2026CV Low-Altitude Target Recognition

## Project Overview

This project focuses on low-altitude target recognition in UAV scenarios.

Current main route:

```text
PX4 + Gazebo Harmonic + QGroundControl + ROS 2 + Python + OpenCV + YOLOv8
```

The project is organized to support two goals:

1. Full system reproduction
2. Vision algorithm reproduction
3. ROS 2 integration and perception pipeline reproduction

## Repository Structure

```text
.
├─ docs/
│  ├─ README.md
│  ├─ ROS2_RUNBOOK.md
│  ├─ ROS2_RESUME_PLAN.md
│  └─ SIM_TRAINING_PIPELINE.md      # spawn → collect → train → deploy
├─ sim/
│  ├─ README.md
│  ├─ configs/target_models.yaml    # YOLO classes + Fuel models
│  ├─ launch/spawn_targets.py       # randomise targets in baylands
│  ├─ missions/random_waypoints.py  # MAVSDK random-waypoint flight
│  └─ runtime/                      # generated spawn manifests
├─ ros2_ws/
│  ├─ README.md
│  └─ src/
│     └─ low_altitude_bringup/
├─ vision/
│  ├─ README.md
│  ├─ requirements.txt
│  ├─ requirements-train.txt        # 训练 venv 依赖清单（Windows）
│  ├─ setup_train_env.ps1           # Windows 训练 venv（PyTorch CUDA 12.1）
│  ├─ setup_infer_env.sh            # Linux 推理 venv（CPU 默认 / CUDA 可选）
│  ├─ train_sim.py                  # YOLOv8s fine-tune entry point
│  ├─ summarize_results.py          # JSONL → Markdown report
│  ├─ Dockerfile
│  ├─ run_detection.py
│  └─ dataset/
│     ├─ projection.py              # 3D AABB → 2D bbox
│     ├─ build_yolo_dataset.py      # train/val split + dataset.yaml
│     └─ test_projection.py
├─ demo/
│  ├─ README.md
│  ├─ test_images/
│  ├─ outputs/
│  └─ demo_video/
├─ scripts/
│  └─ run_demo.sh
├─ PROJECT_PROGRESS.md
├─ PRESENTATION_SCRIPT.md
└─ README.md
```

## Current Status

Project now runs entirely on **native Ubuntu 24.04** (migrated from
`Windows 11 + WSL2`). Project root is `/home/libo/2026CV`, PX4 source is at
`~/PX4/PX4-Autopilot`, ROS 2 distro is **Jazzy**, and Python ML/CV code is
isolated inside the `vision/.venv-train` virtualenv.

Completed:

1. Native Ubuntu 24.04 environment
2. PX4 v1.16.0 source at `~/PX4/PX4-Autopilot`
3. Gazebo Harmonic (gz sim 8.x) installed
4. `px4_sitl gz_x500` startup verified previously under WSL
5. QGroundControl connection verified previously under WSL
6. ROS 2 Jazzy workspace scaffold (rebuild required after migration)

Next:

1. Bridge Gazebo camera topics into ROS 2
2. Connect YOLOv8 as a ROS 2 perception node
3. Add PX4 ROS 2 interfaces and control logic

## Quick Links

- Project documents are indexed in [docs/README.md](./docs/README.md).
- ROS 2 workspace notes live in [ros2_ws/README.md](./ros2_ws/README.md).
- ROS 2 runtime notes live in [docs/ROS2_RUNBOOK.md](./docs/ROS2_RUNBOOK.md).
- **Sim → train → deploy pipeline**: [docs/SIM_TRAINING_PIPELINE.md](./docs/SIM_TRAINING_PIPELINE.md).
- Project progress: [PROJECT_PROGRESS.md](./PROJECT_PROGRESS.md).
- Presentation script: [PRESENTATION_SCRIPT.md](./PRESENTATION_SCRIPT.md).

## Real-time Detection Demo

On native Ubuntu 24.04 (PX4 SITL must already be running):

```bash
# 一次性激活 ROS + venv（推荐放进 ~/.bashrc）
source scripts/activate_env.sh
bash scripts/run_demo.sh
```

This launches a 3-process pipeline: `parameter_bridge` (clock), `gz_camera_bridge`
(image), and `yolo_detector` (inference + HUD overlay + rich dashboard, all in
one process). View the annotated stream with
`ros2 run rqt_image_view rqt_image_view /camera/annotated`.

## Reproduction Strategy

This repository supports two reproduction paths:

1. Full reproduction
   Set up native Ubuntu, PX4, Gazebo Harmonic, and QGroundControl, then run the complete UAV simulation workflow.

2. Vision-only reproduction
   Use the `vision/` folder to reproduce the detection environment and algorithm results independently.

## Migration notes (Windows/WSL → native Ubuntu)

- All hardcoded `/mnt/d/2026CV` and `D:\2026CV` paths now point to
  `/home/libo/2026CV`.
- Default ROS distro switched from `humble` (22.04) to `jazzy` (24.04).
- **Hybrid training/inference split**: the Linux install currently boots
  inside a VirtualBox VM, which does not expose the host RTX 4050 (no GPU
  PCIe passthrough). YOLOv8 **training therefore stays on Windows** via
  [vision/setup_train_env.ps1](./vision/setup_train_env.ps1) (CUDA 12.1),
  while the Linux side keeps a CPU-only **inference** venv via
  [vision/setup_infer_env.sh](./vision/setup_infer_env.sh). Both create
  `vision/.venv-train/` on their respective host. The trained `best.pt`
  is copied into `ros2_ws/` on the Linux side for the ROS 2
  `yolo_detector` node, which still needs `torch`+`ultralytics` at
  runtime to load the weights and run forward passes.
