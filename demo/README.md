# 演示资源说明

`demo/` 目录用于存放演示相关资源。

建议用途：

1. `test_images/`：测试图片
2. `outputs/`：旧版共享文件方案输出
3. `ros2_outputs/`：ROS 2 图像快照与调试输出
4. `demo_video/`：演示视频

## 实时检测 + 监控仪表板

一键启动（在 Ubuntu 24.04 中，PX4 SITL 需先在另一个终端运行）：

```bash
bash ../scripts/run_demo.sh
```

包含（3 个进程）：

- `parameter_bridge`：Gazebo `/clock` 桥接
- `gz_camera_bridge`：相机图像桥接到 `/camera/image_raw`
- `yolo_detector`：YOLOv8 推理 + HUD 叠加 + rich 仪表盘（三合一）
  - 发布 `/detections/yolo`、`/camera/annotated`（带检测框 + FPS/延迟/状态徽标 HUD）
  - 同进程终端输出 rich 表格实时统计

查看带 HUD 的画面：`ros2 run rqt_image_view rqt_image_view /camera/annotated`。

## 实验成果文件

`yolo_detector` 在运行时会持续把可分析的实验数据写入 `demo/ros2_outputs/`：

- `detections.jsonl`：每帧推理 JSON 行（含 `latency_ms`、`detections` 列表）
- `summary.json`：周期刷新的总览（FPS、p95 延迟、各类别累计计数）

跑完后可以离线生成 Markdown 报告（含类别分布、延迟直方图）：

```bash
python vision/summarize_results.py \
  --jsonl demo/ros2_outputs/detections.jsonl \
  --output demo/ros2_outputs/report.md
```
