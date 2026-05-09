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
│  ├─ requirements-train.txt        # Windows training venv
│  ├─ setup_train_env.ps1           # CUDA 12.1 + ultralytics installer
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
├─ REPORT_SHARED_DEMO.md
└─ README.md
```

## Current Status

Completed:

1. WSL2 + Ubuntu 22.04 environment setup
2. PX4 v1.16.0 setup
3. Gazebo Harmonic setup
4. `px4_sitl gz_x500` startup
5. QGroundControl connection
6. ROS 2 Humble workspace scaffold and build validation

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

From WSL Ubuntu 22.04 (PX4 SITL must already be running):

```bash
bash scripts/run_demo.sh
```

This launches a 3-process pipeline: `parameter_bridge` (clock), `gz_camera_bridge`
(image), and `yolo_detector` (inference + HUD overlay + rich dashboard, all in
one process). View the annotated stream with
`ros2 run rqt_image_view rqt_image_view /camera/annotated`.

## Reproduction Strategy

This repository supports two reproduction paths:

1. Full reproduction
   Set up WSL2, PX4, Gazebo Harmonic, and QGroundControl, then run the complete UAV simulation workflow.

2. Vision-only reproduction
   Use the `vision/` folder to reproduce the detection environment and algorithm results independently.
