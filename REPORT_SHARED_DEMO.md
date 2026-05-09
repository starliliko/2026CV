# 低空目标识别项目

---

## 1. 目标

在无人机低空仿真场景中：

稳定获取云台实时画面

并为 YOLOv8 检测提供输入

---

## 2. 当前进展

1. WSL2 + Ubuntu 22.04 已完成
2. PX4 v1.16.0 + Gazebo Harmonic 已联调
3. QGroundControl 已连接
4. 云台相机话题已获取
5. 共享文件链路已稳定运行

---

## 3. 本次演示链路

PX4 SITL + Gazebo

-> WSL 订阅云台图像

-> 写入共享目录循环缓冲

-> Windows OpenCV 实时显示

---

## 4. 现场命令 A：启动仿真

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500_gimbal
```

---

## 5. 现场命令 B：启动写帧（WSL）

```bash
cd /mnt/d/2026CV
python3 vision/save_gz_camera_frame.py --world default --model x500_gimbal_0
```

预期：终端持续出现 `saved frame N`

---

## 6. 现场命令 C：启动显示（Windows）

```powershell
cd D:\2026CV
python vision\view_shared_camera_windows.py
```

预期：弹窗 `Gazebo Onboard Camera`，显示实时云台画面

---

## 8. 备选命令（baylands 世界）

```bash
python3 vision/save_gz_camera_frame.py --world baylands --model x500_gimbal_0
```

---

## 9. 下一步

1. 迁移到 ROS 2 图像话题链路
2. 接入 YOLOv8 并发布检测结果
3. 记录帧率、延迟和稳定性指标
4. 扩展跟踪或简易闭环控制

---

## 10. 结束语

我们已完成仿真、通信和云台画面获取的稳定打通。

当前方案现场展示，后续将接入 ROS 2 与 YOLOv8。
2
