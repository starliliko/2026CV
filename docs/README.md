# 文档导航

## 文档列表

1. [项目当前进展汇报](../PROJECT_PROGRESS.md)
2. [3分钟汇报稿](../PRESENTATION_SCRIPT.md)
3. [ROS 2 运行手册](./ROS2_RUNBOOK.md)
4. [ROS 2 进度恢复计划](./ROS2_RESUME_PLAN.md)
5. [仿真训练 → 部署端到端流程](./SIM_TRAINING_PIPELINE.md)
6. [系统卡死排障结论（内存与 swap）](./SYSTEM_FREEZE_ROOT_CAUSE.md)

## 使用建议

如果是组内协作，建议按下面顺序阅读：

1. 先看 ROS 2 运行手册（如何把仿真+检测拉起来）
2. 再看项目进展
3. 最后看汇报稿

## 实时演示

一键启动实时检测 + HUD 叠加 + 终端仪表盘（三进程合并版）：

```bash
bash ../scripts/run_demo.sh
```

查看带 HUD 的图像：`ros2 run rqt_image_view rqt_image_view /camera/annotated`。

当前的实时链路已经合并到 `yolo_detector` 内部，不再需要独立的
`frame_monitor` / `detection_overlay` / `perception_dashboard` 节点。

## 后续计划

后续可以继续补充以下文档：

1. 相机图像获取说明
2. YOLOv8 接入说明
3. 实验结果记录
4. 常见问题排查说明
