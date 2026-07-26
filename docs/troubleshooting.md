# 常见问题与排障

## Gazebo 没有相机话题

```bash
gz topic -l | grep -E 'camera|image'
```

如果没有结果，先确认 PX4/Gazebo 已启动、仿真未暂停，并检查所选世界和模型名称。`gz_image_topic` 必须与实际话题完全一致。

## `/clock` 存在但 ROS 2 没有图像

检查 Gazebo 图像话题和 ROS 2 话题：

```bash
gz topic -l | grep image
ros2 topic list | grep camera
ros2 topic hz /camera/image_raw
```

默认相机路径基于 `baylands_2026cv` 和 `x500_gimbal_0`。切换世界后应同步修改启动参数。

## 检测节点提示模型不可用

```bash
source vision/.venv-train/bin/activate
bash scripts/download_model.sh
python -c "import torch, ultralytics; print(torch.__version__)"
```

然后确认启动参数中的 `model_path` 指向真实文件。

## 推理越来越慢或内存持续增长

优先降低输入压力：

```bash
THROTTLE_HZ=3 IMGSZ=320 DEVICE=cpu bash scripts/launch_all.sh
```

同时关闭不必要的磁盘日志，观察内存和 Swap：

```bash
watch -n 1 free -h
bash scripts/quick_health_check.sh
```

项目已经加入最新帧限流，避免检测节点落后时积压大量图像消息。完整问题记录见：

- [SYSTEM_FREEZE_ROOT_CAUSE.md](SYSTEM_FREEZE_ROOT_CAUSE.md)
- [SYSTEM_FREEZE_END_TO_END_REPORT.md](SYSTEM_FREEZE_END_TO_END_REPORT.md)

## VirtualBox 中 CUDA 不可用

这是当前环境的已知限制。模型训练应在 Windows 宿主机进行；Ubuntu 虚拟机使用 CPU 推理。不要仅通过安装 CUDA Toolkit 判断可用性，应以以下结果为准：

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## `gz sim` 子命令不可见

```bash
source scripts/activate_env.sh
GZ_CONFIG_PATH=/usr/share/gz gz --commands | grep -E '^  sim:'
```

项目环境脚本会将 `/usr/share/gz` 加入 `GZ_CONFIG_PATH`。
