# 演示与运行输出

ROS 2 检测节点默认将以下文件写入 `demo/ros2_outputs/`：

- `detections.jsonl`：逐帧检测结果与延迟
- `summary.json`：滚动运行指标
- `report.md`：通过 `vision/summarize_results.py` 生成的离线报告
- 可选的标注图片和启动日志

这些运行文件可能快速增大，因此默认不提交到 Git。用于仓库首页展示的精选截图或短视频可以单独放在 `demo/screenshots/` 和 `demo/videos/`。
